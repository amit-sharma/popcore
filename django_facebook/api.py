from django.forms.util import ValidationError
from django.utils import simplejson as json
from django.db import transaction
from django_facebook import settings as facebook_settings
from django_facebook.utils import mass_get_or_create, cleanup_oauth_url, \
	parse_signed_request, get_data_arr
from open_facebook.exceptions import OpenFacebookException
import datetime
import logging
import sys
import urllib
from open_facebook import exceptions as open_facebook_exceptions
from open_facebook.utils import send_warning, json
from open_facebook.api import FacebookAuthorization
from django.db import connection, IntegrityError
from threading import Thread
from django.conf import settings
from bulkops import insert_many
import pprint
logger = logging.getLogger(__name__)

def fetchMovieLikes(data):
    usr_id, fid_list, graph,i = data
    NUM_CATEGORIES=4
    batchstr_array = []
    for fid in fid_list:
        batchstr_array.append('{"method":"GET","relative_url":"%s/movies?fields=link,name,category,likes,app_id,release_date"},{"method":"GET","relative_url":"%s/music?fields=link,name,category,likes,app_id,release_date"},{"method":"GET","relative_url":"%s/books?fields=link,name,category,likes,app_id,release_date"},{"method":"GET","relative_url":"%s/television?fields=link,name,category,likes,app_id,release_date"}' %(fid,fid,fid,fid))   
    batchstr = '['+ ','.join(batchstr_array) + ']'
    #print batchstr
    postdata={'batch':batchstr}
    db_insert_list=[]
    try:
        fb_response= graph.request(post_data=postdata)
       
        #print "yo, look mamovies",type(fb_response[0]['body'])
        
        for j in range(len(fid_list)):
            insert_items_list = []
            for k in range(NUM_CATEGORIES):
                fr_items_str = fb_response[j*NUM_CATEGORIES+k]['body']
                fr_items = json.loads(fr_items_str)
                #print fr_movies['data']
                #['body']['data']
                if (fr_items['data'] is not None) and (len(fr_items['data']) > 0):
                    insert_items_list.extend(fr_items['data'])
                    #FacebookUserConverter.store_foreachfriend(usr_id, fid_list[j], fr_items['data'])
            db_inserts = FacebookUserConverter.store_foreachfriend(usr_id, fid_list[j], insert_items_list)
            db_insert_list.extend(db_inserts)
           
    except (TypeError,IOError) as e:
        print "Type error", e 
        
    try:
        insert_many(db_insert_list)
    except IntegrityError,ie:
        print "in fetchMovieLikes(api.py):",ie
    finally:
        connection.close()   
    """fb_response = graph.get("/" +fid+ "/likes", fields="link,name,category") 
    fr_movies = fb_response['data']
    FacebookUserConverter.store_foreachfriend(usr_id, fid, fr_movies)"""
    #print "Done",i


def get_persistent_graph(request, *args, **kwargs):
    '''
    Wraps itself around get facebook graph
    But stores the graph in the session, allowing usage across multiple pageviews
    Note that Facebook session's expire at some point, you can't store this for permanent usage
    Atleast not without asking for the offline_access permission
    '''
    if not request:
        raise ValidationError, 'Request is required if you want to use persistent tokens'
    
    if hasattr(request, 'facebook'):
        graph = request.facebook
        _add_current_user_id(graph, request.user)
        return graph
        
    #get the new graph
    graph = get_facebook_graph(request, *args, **kwargs)
    
    #if it's valid replace the old cache
    if graph is not None and graph.access_token:
        request.session['graph'] = graph
    else:
        facebook_open_graph_cached = request.session.get('graph')
        if facebook_open_graph_cached:
            facebook_open_graph_cached._me = None
        graph = facebook_open_graph_cached   
        
    _add_current_user_id(graph, request.user)
    request.facebook = graph
        
    return graph
        
    

def get_facebook_graph(request=None, access_token=None, redirect_uri=None, raise_=False):
    '''
    given a request from one of these
    - js authentication flow (signed cookie)
    - facebook app authentication flow (signed cookie)
    - facebook oauth redirect (code param in url)
    - mobile authentication flow (direct access_token)
    - offline access token stored in user profile

    returns a graph object

    redirect path is the path from which you requested the token
    for some reason facebook needs exactly this uri when converting the code
    to a token
    falls back to the current page without code in the request params
    specify redirect_uri if you are not posting and recieving the code
    on the same page
    '''
    # this is not a production flow, but very handy for testing
    if not access_token and request.REQUEST.get('access_token'):
        access_token = request.REQUEST['access_token']
    # should drop query params be included in the open facebook api,
    # maybe, weird this...
    from open_facebook import OpenFacebook, FacebookAuthorization
    from django.core.cache import cache
    expires = None
    if hasattr(request, 'facebook') and request.facebook:
        graph = request.facebook
        _add_current_user_id(graph, request.user)
        return graph

    # parse the signed request if we have it
    signed_data = None
    if request:
        signed_request_string = request.REQUEST.get('signed_data')
        if signed_request_string:
            logger.info('Got signed data from facebook')
            signed_data = parse_signed_request(signed_request_string)
        if signed_data:
            logger.info('We were able to parse the signed data')

    # the easy case, we have an access token in the signed data
    if signed_data and 'oauth_token' in signed_data:
        access_token = signed_data['oauth_token']

    if not access_token:
        # easy case, code is in the get
        code = request.REQUEST.get('code')
        if code:
            logger.info('Got code from the request data')

        if not code:
            # signed request or cookie leading, base 64 decoding needed
            cookie_name = 'fbsr_%s' % facebook_settings.FACEBOOK_APP_ID
            cookie_data = request.COOKIES.get(cookie_name)

            if cookie_data:
                signed_request_string = cookie_data
                if signed_request_string:
                    logger.info('Got signed data from cookie')
                signed_data = parse_signed_request(signed_request_string)
                if signed_data:
                    logger.info('Parsed the cookie data')
                # the javascript api assumes a redirect uri of ''
                redirect_uri = ''

            if signed_data:
                # parsed data can fail because of signing issues
                if 'oauth_token' in signed_data:
                    logger.info('Got access_token from parsed data')
                    # we already have an active access token in the data
                    access_token = signed_data['oauth_token']
                else:
                    logger.info('Got code from parsed data')
                    # no access token, need to use this code to get one
                    code = signed_data.get('code', None)

        if not access_token:
	    import hashlib
            if code:
                cache_key = 'convert_code_%d' % int(hashlib.md5(code).hexdigest(), 16)
		logger.info(pprint.pformat(cache)+cache_key)
                access_token = cache.get(cache_key)
                if not access_token:
                    # exchange the code for an access token
                    # based on the php api
                    # https://github.com/facebook/php-sdk/blob/master/src/base_facebook.php
                    # create a default for the redirect_uri
                    # when using the javascript sdk the default
                    # should be '' an empty string
                    # for other pages it should be the url
                    if not redirect_uri:
                        redirect_uri = ''

                    # we need to drop signed_data, code and state
                    redirect_uri = cleanup_oauth_url(redirect_uri)

                    try:
                        logger.info(
                            'trying to convert the code with redirect uri: %s',
                            redirect_uri)
                        # This is realy slow, that's why it's cached
                        token_response = FacebookAuthorization.convert_code(
                            code, redirect_uri=redirect_uri)
                        expires = token_response.get('expires')
                        access_token = token_response['access_token']
                        # would use cookies instead, but django's cookie setting
                        # is a bit of a mess
                        cache.set(cache_key, access_token, 60 * 60 * 2)
                    except open_facebook_exceptions.OAuthException, e:
                        # this sometimes fails, but it shouldnt raise because
                        # it happens when users remove your
                        # permissions and then try to reauthenticate
                        logger.warn('Error when trying to convert code %s',
                                    unicode(e))
                        if raise_:
                            raise
                        else:
                            return None
            elif request.user.is_authenticated():
                # support for offline access tokens stored in the users profile
                profile = request.user.get_profile()
                access_token = getattr(profile, 'access_token', None)
                if not access_token:
                    if raise_:
                        message = 'Couldnt find an access token in the request or the users profile'
                        raise open_facebook_exceptions.OAuthException(message)
                    else:
                        return None
            else:
                if raise_:
                    message = 'Couldnt find an access token in the request or cookies'
                    raise open_facebook_exceptions.OAuthException(message)
                else:
                    return None

    graph = OpenFacebook(access_token, signed_data, expires=expires)
    # add user specific identifiers
    if request:
        _add_current_user_id(graph, request.user)

    return graph

def _add_current_user_id(graph, user):
    '''
    set the current user id, convenient if you want to make sure you fb session and user belong together
    '''
    if graph:
        graph.current_user_id = None
        
    if user.is_authenticated() and graph:
        profile = user.get_profile()
        facebook_id = getattr(profile, 'facebook_id', None)
        if facebook_id:
            graph.current_user_id = facebook_id

class FacebookUserConverter(object):
    '''
    This conversion class helps you to convert Facebook users to Django users
    
    Helps with
    - extracting and prepopulating full profile data
    - invite flows
    - importing and storing likes
    '''
    def __init__(self, open_facebook):
        from open_facebook.api import OpenFacebook
        self.open_facebook = open_facebook
        assert isinstance(open_facebook, OpenFacebook)
        self._profile = None

    def is_authenticated(self):
        return self.open_facebook.is_authenticated()

    def facebook_registration_data(self, username=True):
        '''
        Gets all registration data
        and ensures its correct input for a django registration
        '''
        facebook_profile_data = self.facebook_profile_data()
        user_data = {}
        try:
            user_data = self._convert_facebook_data(facebook_profile_data, username=username)
        except OpenFacebookException, e:
            self._report_broken_facebook_data(user_data, facebook_profile_data, e)
            raise

        return user_data
    
    def facebook_profile_data(self):
        '''
        Returns the facebook profile data, together with the image locations
        '''
        if self._profile is None:
            profile = self.open_facebook.me()
            profile['image'] = self.open_facebook.my_image_url('large')
            profile['image_thumb'] = self.open_facebook.my_image_url()
            self._profile = profile
        return self._profile

    @classmethod
    def _convert_facebook_data(cls, facebook_profile_data, username=True):
        '''
        Takes facebook user data and converts it to a format for usage with Django
        '''
        user_data = facebook_profile_data.copy()
        profile = facebook_profile_data.copy()
        website = profile.get('website')
        if website:
            user_data['website_url'] = cls._extract_url(website)
            
        user_data['facebook_profile_url'] = profile.get('link')
        user_data['facebook_name'] = profile.get('name')
        if len(user_data.get('email', '')) > 75:
            #no more fake email accounts for facebook
            del user_data['email']
        
        gender = profile.get('gender', None)
         
        if gender == 'male':
            user_data['gender'] = 'm'
        elif gender == 'female':
            user_data['gender'] = 'f'

        user_data['username'] = cls._retrieve_facebook_username(user_data)
        user_data['password2'] = user_data['password1'] = cls._generate_fake_password()

        facebook_map = dict(birthday='date_of_birth', about='about_me', id='facebook_id')
        for k, v in facebook_map.items():
            user_data[v] = user_data.get(k)
        user_data['facebook_id'] = int(user_data['facebook_id'])

        if not user_data['about_me'] and user_data.get('quotes'):
            user_data['about_me'] = user_data.get('quotes')
            
        user_data['date_of_birth'] = cls._parse_data_of_birth(user_data['date_of_birth'])
        
        if username:
            user_data['username'] = cls._create_unique_username(user_data['username'])

        return user_data

    @classmethod
    def _extract_url(cls, text_url_field):
        '''
        >>> url_text = 'http://www.google.com blabla'
        >>> FacebookAPI._extract_url(url_text)
        u'http://www.google.com/'
        
        >>> url_text = 'http://www.google.com/'
        >>> FacebookAPI._extract_url(url_text)
        u'http://www.google.com/'
        
        >>> url_text = 'google.com/'
        >>> FacebookAPI._extract_url(url_text)
        u'http://google.com/'
        
        >>> url_text = 'http://www.fahiolista.com/www.myspace.com/www.google.com'
        >>> FacebookAPI._extract_url(url_text)
        u'http://www.fahiolista.com/www.myspace.com/www.google.com'
        
        >>> url_text = u"""http://fernandaferrervazquez.blogspot.com/\r\nhttp://twitter.com/fferrervazquez\r\nhttp://comunidad.redfashion.es/profile/fernandaferrervazquez\r\nhttp://www.facebook.com/group.php?gid3D40257259997&ref3Dts\r\nhttp://fernandaferrervazquez.spaces.live.com/blog/cns!EDCBAC31EE9D9A0C!326.trak\r\nhttp://www.linkedin.com/myprofile?trk3Dhb_pro\r\nhttp://www.youtube.com/account#profile\r\nhttp://www.flickr.com/\r\n Mi galer\xeda\r\nhttp://www.flickr.com/photos/wwwfernandaferrervazquez-showroomrecoletacom/ \r\n\r\nhttp://www.facebook.com/pages/Buenos-Aires-Argentina/Fernanda-F-Showroom-Recoleta/200218353804?ref3Dts\r\nhttp://fernandaferrervazquez.wordpress.com/wp-admin/"""        
        >>> FacebookAPI._extract_url(url_text)
        u'http://fernandaferrervazquez.blogspot.com/a'
        '''
        import re
        text_url_field = text_url_field.encode('utf8')
        seperation = re.compile('[ ,;\n\r]+')
        parts = seperation.split(text_url_field)
        for part in parts:
            from django.forms import URLField
            url_check = URLField(verify_exists=False)
            try:
                clean_url = url_check.clean(part)
                return clean_url
            except ValidationError, e:
                continue

    @classmethod
    def _generate_fake_password(cls):
        '''
        Returns a random fake password
        '''
        import string
        from random import choice
        size = 9
        password = ''.join([choice(string.letters + string.digits) for i in range(size)])
        return password.lower()


    @classmethod
    def _parse_data_of_birth(cls, data_of_birth_string):
        if data_of_birth_string:
            format = '%m/%d/%Y'
            try:
                parsed_date = datetime.datetime.strptime(data_of_birth_string, format)
                return parsed_date
            except ValueError:
                #Facebook sometimes provides a partial date format ie 04/07 (ignore those)
                if data_of_birth_string.count('/') != 1:
                    raise

    @classmethod
    def _report_broken_facebook_data(cls, facebook_data, original_facebook_data, e):
        '''
        Sends a nice error email with the 
        - facebook data
        - exception
        - stacktrace
        '''
        from pprint import pformat
        data_dump = json.dumps(original_facebook_data)
        data_dump_python = pformat(original_facebook_data)
        message_format = 'The following facebook data failed with error %s\n\n json %s \n\n python %s \n'
        data_tuple = (unicode(e), data_dump, data_dump_python)
        message = message_format % data_tuple
        extra_data = {
             'data_dump': data_dump,
             'data_dump_python': data_dump_python,
             'facebook_data': facebook_data,            
        }
        send_warning(message, **extra_data)

    @classmethod
    def _create_unique_username(cls, base_username):
        '''
        Check the database and add numbers to the username to ensure its unique
        '''
        from django.contrib.auth.models import User
        usernames = list(User.objects.filter(username__istartswith=base_username).values_list('username', flat=True))
        usernames_lower = [str(u).lower() for u in usernames]
        username = str(base_username)
        i = 1
        while base_username.lower() in usernames_lower:
            base_username = username + str(i)
            i += 1
        return base_username

    @classmethod
    def _retrieve_facebook_username(cls, facebook_data):
        '''
        Search for the username in 3 places
        - public profile
        - email
        - name
        '''
        link = facebook_data.get('link')
        if link:
            username = link.split('/')[-1]
            username = cls._username_slugify(username)
        if 'profilephp' in username:
            username = None

        if not username and 'email' in facebook_data:
            username = cls._username_slugify(facebook_data.get('email').split('@')[0])
        
        if not username or len(username) < 4:
            username = cls._username_slugify(facebook_data.get('name'))

        return username

    @classmethod
    def _username_slugify(cls, username):
        '''
        Slugify the username and replace - with _ to meet username requirements
        '''
        from django.template.defaultfilters import slugify
        return slugify(username).replace('-', '_')
    
    def get_and_store_likes(self, user):
        '''
        Gets and stores your facebook likes to DB
        Both the get and the store run in a async task when
        FACEBOOK_CELERY_STORE = True
        '''
        if facebook_settings.FACEBOOK_CELERY_STORE:
            from django_facebook.tasks import get_and_store_likes
            print "fb processing starting:api.py"  
            get_and_store_likes.delay(user, self)
        else:
            self._get_and_store_likes(user)
    
    def _get_and_store_likes(self, user):
        likes = self.get_likes()
        stored_likes = self._store_likes(user, likes)
        return stored_likes
    
    #TODO implement multiquery so that also have created_time stored
    def get_likes(self, limit=1000):
        '''
        Parses the facebook response and returns the likes
        '''
        """
        likes_response = self.open_facebook.fql("SELECT type, page_id, pic, page_url, name, created_time FROM page WHERE page_id IN (SELECT page_id FROM page_fan WHERE uid=me() AND type IN ('{0}','{1}','{2}','{3}'))".format('MOVIE','BOOK','TV SHOW','MUSICIAN/BAND'))
        likes = likes_response and likes_response.get('data')
        logger.info('found %s likes', len(likes))
        return likes"""
        NUM_CATEGORIES=4
        batchstr = '[{"method":"GET","relative_url":"me/movies?fields=link,name,category,likes,app_id,release_date"},{"method":"GET","relative_url":"me/music?fields=link,name,category,likes,app_id,release_date"},{"method":"GET","relative_url":"me/books?fields=link,name,category,likes,app_id,release_date"},{"method":"GET","relative_url":"me/television?fields=link,name,category,likes,app_id,release_date"}]'   
        postdata={'batch':batchstr}
        insert_items_list = []
        try:
            fb_response= self.open_facebook.request(post_data=postdata)
            #print fb_response
            #print "yo, look mamovies",type(fb_response[0]['body'])
            for k in range(NUM_CATEGORIES):
                fr_items_str = fb_response[k]['body']
                fr_items = json.loads(fr_items_str)
                if (fr_items['data'] is not None) and (len(fr_items['data']) > 0):
                    insert_items_list.extend(fr_items['data'])
            
        except (TypeError,IOError) as e:
            print "Type error", e 
        finally:
            connection.close()   
        return insert_items_list
                     
    def store_likes(self, user, likes):
        '''
        Given a user and likes store these in the db
        Note this can be a heavy operation, best to do it in the background using celery
        '''
        if facebook_settings.FACEBOOK_CELERY_STORE:
            from django_facebook.tasks import store_likes
            store_likes.delay(user, likes)
        else:
            self._store_likes(user, likes)
        
    @classmethod
    @transaction.commit_on_success
    def _store_likes(self, user, likes):
        if likes:
            from django_facebook.models import FacebookLike
            from dateutil.parser import parse
            #base_queryset = FacebookLike.objects.filter(user_id=user.id)
            #global_defaults = dict(user_id=user.id)
            #id_field = 'facebook_id'
            #default_dict = {}
            insert_list=[]
            for like in likes:
                name = like.get('name')
                pic = like.get('picture')
                page_url = like.get('link')
                num_likes = like.get('likes')
                
                if like.get('app_id') is not None:
                    continue
                    
                release_date_string = like.get('release_date')
                created_time_string = like.get('created_time')
                created_time = None
                release_date=None
                if created_time_string:
                    created_time = datetime.datetime.strptime(like['created_time'], "%Y-%m-%dT%H:%M:%S+0000")
                if release_date_string:
                    try:
                        release_date = parse(like['release_date'])
                    except ValueError, ve:
                        release_date = None
                new_like_item = FacebookLike(
                    user_id=user.id,
                    facebook_id=like['id'],
                    created_time=created_time,
                    category=like.get('category'),
                    name=name,
                    pic=pic,
                    page_url=page_url,
                    num_likes=num_likes,
                    release_date=release_date
                )
                insert_list.append(new_like_item)
            
            try:
                insert_many(insert_list)
            except IntegrityError, ie:
                print "in _store_likes:",ie
            """current_likes, inserted_likes = mass_get_or_create(
                FacebookLike, base_queryset, id_field, default_dict, global_defaults
            )"""
            #logger.debug('found %s likes and inserted %s new likes', len(current_likes), len(inserted_likes))
               
        return likes
    
    def get_and_store_friends(self, user):
        '''
        Gets and stores your facebook friends to DB
        Both the get and the store run in a async task when
        FACEBOOK_CELERY_STORE = True
        '''
        if facebook_settings.FACEBOOK_CELERY_STORE:
            from django_facebook.tasks import get_and_store_friends
            get_and_store_friends.delay(user, self)
        else:
            self._get_and_store_friends(user)
            
    def _get_and_store_friends(self, user):
        '''
        Getting the friends via fb and storing them
        '''
        friends = self.get_friends()
        stored_friends = self._store_friends(user, friends)
        return stored_friends
        
    def get_friends(self, limit=1000):
        '''
        Connects to the facebook api and gets the users friends
        '''
        friends = getattr(self, '_friends', None)
        if friends is None:
            friends_response = self.open_facebook.fql("SELECT uid, name, sex FROM user WHERE uid IN (SELECT uid2 FROM friend WHERE uid1 = me()) LIMIT %s" % limit)
            #friends_response = self.open_facebook.get('me/friends', limit=limit)
	    friends_temp = get_data_arr(friends_response)
            friends=[]
            for response_dict in friends_temp:
                response_dict['id'] = response_dict['uid']
                friends.append(response_dict)
        
	logger.info('found %s friends', len(friends))
        return friends
    
    def store_friends(self, user, friends):
        '''st     base_runtimeflags

        Stores the given friends locally for this user
        Quite slow, better do this using celery on a secondary db
        '''
        if facebook_settings.FACEBOOK_CELERY_STORE:
            from django_facebook.tasks import store_friends
            store_friends.delay(user, friends)
        else:
            self._store_friends(user, friends)
        
    @classmethod
    @transaction.commit_on_success
    def _store_friends(self, user, friends):
        from django_facebook.models import FacebookUser
        #store the users for later retrieval
        if friends:
            #see which ids this user already stored
            #base_queryset = FacebookUser.objects.filter(user_id=user.id)
            #global_defaults = dict(user_id=user.id)
            #default_dict = {}
            insert_list=[]
            for f in friends:
                name = f.get('name')
                new_fruser = FacebookUser(user_id=user.id, name=name, facebook_id=str(f['id']))
                insert_list.append(new_fruser)
                #default_dict[str(f['id'])] = dict(name=name)
                
            #id_field = 'facebook_id'
            try:
                insert_many(insert_list)
            except IntegrityError, ie:
                print "In _store_friends, IntegrityError:", ie
            """
            current_friends, inserted_friends = mass_get_or_create(
                FacebookUser, base_queryset, id_field, default_dict, global_defaults
            )"""
            #logger.debug('found %s friends and inserted %s new ones', len(current_friends), len(inserted_friends))
                    
        return friends
    
    def get_and_store_friendlikes(self, user):
        '''
        Gets and stores your friends' facebook likes to DB
        Both the get and the store run in a async task when
        FACEBOOK_CELERY_STORE = True
        '''
        if facebook_settings.FACEBOOK_CELERY_STORE:
            from django_facebook.tasks import get_and_store_friendlikes
            get_and_store_friendlikes.delay(user, self)
        else:
            stored_friends = self._get_and_store_friends(user)
            self._get_and_store_friendlikes(user,stored_friends)
    
    def _get_and_store_friendlikes(self, user, friends):
        likes = self.get_friendlikes(user, friends)
        #not needed, get_friendlikes also stores them
        #stored_likes = self._store_friendlikes(user, likes)
        return likes
    """
    def get_friendlikes(self, limit=None):
        '''
        Parses the facebook response and returns the likes--only gets those items who have more than 10 likes
        '''
        types = ['MOVIE','BOOK', 'TV SHOW', 'MUSICIAN/BAND']
        min_fancount = 10
        ret_likes = []
        print "Looping"
        for category in types:
            likes_response = self.open_facebook.fql('{"query1":"SELECT uid, page_id, type, profile_section, created_time FROM page_fan WHERE uid IN (SELECT uid2 FROM friend WHERE uid1 = me() AND strpos(1,uid2)=6) AND type=\'%s\'", "query2":"SELECT page_id, name,pic,page_url,release_date FROM page WHERE page_id IN (SELECT page_id FROM #query1) AND fan_count>10"}' % category)
            print "Looping {0}".format(category)
            likes_data = likes_response and likes_response.get('data')
            likes = likes_data[0]['fql_result_set']
            
            temp_dict = {}
            pages = likes_data[1]['fql_result_set']
            for page in pages:
                temp_dict[str(page['page_id'])] = {};
                temp_dict[str(page['page_id'])]['name'] = page['name']
                temp_dict[str(page['page_id'])]['pic'] = page['pic']
                temp_dict[str(page['page_id'])]['page_url'] = page['page_url']
           
            for like in likes:
                if str(like['page_id']) in temp_dict:
                    like['name'] = temp_dict[str(like['page_id'])]['name']    
                    like['pic'] = temp_dict[str(like['page_id'])]['pic']
                    like['page_url'] = temp_dict[str(like['page_id'])]['page_url']
                    ret_likes.append(like)
            #logger.debug(likes)
        logger.info('found %s likes', len(ret_likes))
        #logger.info('found %s temp pages', len(pages))
        print "wuja", len(ret_likes)
        return ret_likes
    """
    
    def get_friendlikes(self, user, friends, limit=None):
        #from multiprocessing import Process
        flikes = True
        LIMIT_FOR_DISPLAY=100
        BATCH_SIZE = 10
        i=0
        threads=[]
        j=0
        while j < len(friends):
        #while j < LIMIT_FOR_DISPLAY:
            fr_list = friends[j:min(j+BATCH_SIZE,len(friends))]
            frid_list = [str(fr['uid']) for fr in fr_list]
            t = Thread(target=fetchMovieLikes, args=((user.id,frid_list,self.open_facebook,i),))
            t.start()
            if j <LIMIT_FOR_DISPLAY:
                #fetchMovieLikes((user.id,frid_list,self.open_facebook,i))
                threads.append(t)
            j += BATCH_SIZE
            i+=1
            """
            fr_id = str(fr['uid'])
            t = Thread(target=fetchMovieLikes, args=((user.id,fr_id,self.open_facebook,i),))
            t.start()
            threads.append(t)
            #flikes[fr_id] = fr_movies['data']
            #print i, "Done"
            i+= 1"""
        for t in threads:
            t.join()
         
        return flikes       
        
    def store_friendlikes(self, user, likes):
        '''
        Given a user and likes store these in the db
        Note this can be a heavy operation, best to do it in the background using celery
        '''
        if facebook_settings.FACEBOOK_CELERY_STORE:
            from django_facebook.tasks import store_friendlikes
            store_friendlikes.delay(user, likes)
        else:
            #from django_facebook.models import FacebookUser
            #friends = FacebookUser.objects.filter(user_id=user.id)
            self._store_friendlikes(user, likes)
    
    def _store_friendlikes(self, user, flikes):
        for f,v in  flikes.iteritems():
            self._store_foreachfriend(user, f, v)
    """        
    def _store_friendlikes(self, user, likes):
        flikes = {}
        for like in likes:
            if str(like['uid']) not in flikes:
                flikes[str(like['uid'])] =[]
            flikes[str(like['uid'])].append(like)
                
        for f,v in flikes.iteritems():
            self._store_foreachfriend(user, f, v) #assuming likes are also segmented by friends, also write created_time
    """
    @classmethod
    def store_foreachfriend(self, usr_id, friendid, likes):
        insert_list = []
        if likes:
            from django_facebook.models import FacebookFriendLike
            from dateutil.parser import parse
            #base_queryset = FacebookFriendLike.objects.filter(friend_fid=friendid)
            #global_defaults = dict(user_id=usr_id, friend_fid=friendid,app_name=settings.POPCORE_APP_NAME)
            id_field = 'facebook_id'
            
            count =0
            for like in likes:
                name = like.get('name')
                num_likes = like.get('likes')
                page_url = like.get('link')
                created_time_string = like.get('created_time')
                release_date_string = like.get('release_date')
                if like.get('app_id') is not None:
                    #print "Filtered Kohli"
                    continue
                #there are other types such as 'Movie general', 'Movie genre', etc but we ignore them.
                graphApiToFQLType = {'Movie':'MOVIE', 'Musician/band':'MUSICIAN/BAND','Book':'BOOK','Tv show':'TV SHOW'}
                if like['category'] not in graphApiToFQLType:
                    continue
                like['category']=graphApiToFQLType[like['category']]
                #print 'Current ABCDF Type is:',like.get('category')
                created_time = None
                release_date = None
                if created_time_string:
                    created_time = datetime.datetime.strptime(like['created_time'], "%Y-%m-%dT%H:%M:%S+0000")
                if release_date_string:
                    try:
                        release_date = parse(like['release_date'])
                    except ValueError, ve:
                        release_date = None
                new_item = FacebookFriendLike(
                    user_id=usr_id, friend_fid=friendid,app_name=settings.POPCORE_APP_NAME,
                    facebook_id=like.get('id'),
                    created_time=created_time,
                    release_date=release_date,
                    category=like.get('category'),
                    name=name,
                    num_likes=num_likes,
                    page_url=page_url
                )
                count+=1
                insert_list.append(new_item)
                """try:
                    new_item.save()
                except IntegrityError, ie:
                    pass
                """
            #from bulkops import insert_many    
            """current_likes, inserted_likes = mass_get_or_create(
                FacebookFriendLike, base_queryset, id_field, default_dict, global_defaults
            )"""
            #print "Counter is:",count
            
            #logger.debug('found %s likes and inserted %s new likes', len(current_likes), len(inserted_likes))
               
        return insert_list
    
    def get_and_store_tiestrength(self, user):
        if facebook_settings.FACEBOOK_CELERY_STORE:
            from django_facebook.tasks import get_and_store_tiestrength
            get_and_store_tiestrength.delay(user, self)
        else:
            self._get_and_store_friends(user)
            
    @transaction.commit_on_success     
    def _get_and_store_tiestrength(self, user):
        import operator
        from django_facebook.models import FacebookUser
        user_freq = self.analyzeUserFeed(user.get_profile().facebook_id)
        close_frlist = sorted(user_freq.iteritems(), key=operator.itemgetter(1), reverse=True)
        rank = 1
        for key, score in close_frlist:
            fr_rows = FacebookUser.objects.filter(user_id=user.id).filter(facebook_id=key)
            if len(fr_rows) > 0:
                fr_row = fr_rows[0]
                #print "Friend id",fr_row.facebook_id
                fr_row.tie_rank = score
                fr_row.save()
                rank += 1
    
        return close_frlist
        
    def analyzeUserFeed(self, user_fbid):
        fqlstr = '{"query1": "SELECT post_id, actor_id, target_id, tagged_ids FROM stream WHERE source_id=%s AND app_id=\'\' LIMIT 100", "query2": "SELECT fromid from comment WHERE post_id IN (SELECT post_id FROM #query1)"}' %(user_fbid)
        fb_response = self.open_facebook.fql(fqlstr)
        wall_updates = get_data_arr(fb_response)[0]['fql_result_set']
        comments = get_data_arr(fb_response)[1]['fql_result_set']
        user_freq={}
        for update in wall_updates:
            if str(update['actor_id']) != str(user_fbid):
                print "1",update['actor_id']
                if str(update['actor_id']) not in user_freq:
                    user_freq[str(update['actor_id'])] = 0
                user_freq[str(update['actor_id'])] += 1
                continue
            else:
                if update['target_id'] is not None and str(update['target_id']) != str(user_fbid):
                    if update['target_id'] not in user_freq:
                        user_freq[update['target_id']] = 0
                    user_freq[update['target_id']] += 1
                for tag_id in update['tagged_ids']:
                    if str(tag_id) != str(user_fbid):
                        if str(tag_id) not in user_freq:
                            user_freq[str(tag_id)] = 0
                        user_freq[str(tag_id)] += 1
            
        for com in comments:
            if str(com['fromid']) != str(user_fbid):
                if str(com['fromid']) not in user_freq:
                    user_freq[str(com['fromid'])] = 0
                user_freq[str(com['fromid'])] += 1
        return user_freq

    def registered_friends(self, user):
        '''
        Returns all profile models which are already registered on your site
        
        and a list of friends which are not on your site
        '''
        from django_facebook.utils import get_profile_class
        profile_class = get_profile_class()
        friends = self.get_friends(limit=1000)
        
        if friends:
            friend_ids = [f['id'] for f in friends]
            friend_objects = profile_class.objects.filter(facebook_id__in=friend_ids).select_related('user')
            registered_ids = [f.facebook_id for f in friend_objects]
            new_friends = [f for f in friends if f['id'] not in registered_ids]
        else:
            new_friends = []
            friend_objects = profile_class.objects.none()
            
        return friend_objects, new_friends
    
    
