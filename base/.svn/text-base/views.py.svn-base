# Create your views here.
# Main file that renders the views in the BASE app.

# Amit Sharma

from django.http import HttpResponse
from django.template import loader, Context, RequestContext
from django.shortcuts import render_to_response, redirect
from django.views.decorators.csrf import csrf_exempt
from django_facebook.models import FacebookUser, FacebookLike, FacebookFriendLike
from django_facebook.api import get_facebook_graph
from django_facebook.views import connect
from base.models import UserProfile, Suggestion, UIConfig
from base.utils import log_activity
from recommender.algorithms import RecOwnLikes, RecConfig
from django_facebook.decorators import facebook_login_required
#import scipy
import re
from pprint import pprint, pformat
import urllib2
import json

#Function to call when a user is authenticated. If he is not, then it returns an error.
@csrf_exempt
#@facebook_login_required
def home(request):
    from json import dumps
    #d={}
    #t = loader.get_template('base/index.html')
    #c = Context({'d':d})
    #return HttpResponse(t.render(c))
    #return render_to_response("base/index.html", context_instance=RequestContext(request))
    if request.user.is_authenticated():
        user=request.user.get_profile()
        log_activity(user.facebook_id, 'view_home')
        #return render_to_response(request,context_instance=RequestContext(request))
        friends = FacebookUser.objects.filter(user_id=user.user_id)
        likes = FacebookLike.objects.filter(user_id=user.user_id)
        #import pdb; pdb.set_trace()
        
        friends_json = []
        for friend in friends:
            fr = {}
            fr['label'] = friend.name
            fr['id'] = friend.facebook_id
            friends_json.append(fr)
        
        uiconf_rows = UIConfig.objects.filter(user=request.user.id)
        if uiconf_rows:
            uiconf = uiconf_rows[0]
        else:
            uiconf = UIConfig(user=request.user.id)
            uiconf.save()
            
        d={'name':user.facebook_name, 'friends': friends, 'likes':likes, 'friends_json':dumps(friends_json), 'uiconfig':uiconf}
        return render_to_response("base/home.html", d,context_instance=RequestContext(request))
    else:
        return HttpResponse("Sorry problem with authentication.")

#Called as the default. Redirects to home if authenticated, else shows a generic non-personal page.
@csrf_exempt    
def landing(request):
    #graph = get_facebook_graph(request)
    #user_fb_profile = graph.me()
    #if user_fb_profile is not None:
    if request.user.is_authenticated():
            #request.GET.setdefault('facebook_login', 1)
            #connect(request)
        
        #return render_to_response(request, context_instance=RequestContext(request))
        return redirect('base.views.home')
    else:
        return render_to_response("base/index.html", {'curr_user1':request.user}, context_instance=RequestContext(request))

#Helper function to get a image for a facebook page. Need this workaround because facebook does not allow FBCDN images to used in fb stream.
@csrf_exempt    
def get_imageshack(request):
    picurl = request.REQUEST['img_url']
    import urllib
    import xml.dom.minidom
    result = urllib.urlopen('http://www.imageshack.us/upload_api.php?url={0}&key=016BKMRV5ef1ba27fb9517682cf9143f4921d482'.format(picurl))
    dom = xml.dom.minidom.parseString(result.read())
    element = dom.getElementsByTagName('image_link')[0]
    ret_url = element.firstChild.nodeValue
    return HttpResponse(ret_url)
    #return HttpResponse(result)

#function to view profile of a user
def view_profile(request):
    fbuser = request.user.get_profile()
    log_activity(fbuser.facebook_id, 'view_profile')
    userprofile = UserProfile.objects.get(facebook_id = fbuser.facebook_id)
    #graph = get_facebook_graph(request)
    #config = RecConfig(max_items=5)
    #algo = RecOwnLikes(request.user, graph, config)
    #likes = algo.recommend()
    #print likes
    likes=None
    suggests = Suggestion.objects.filter(source_user=fbuser.facebook_id)
    #print suggests
    #return HttpResponse(likes)
    return render_to_response('base/userprofile.html', {'userprofile':userprofile, 'likes':likes, 'suggests':suggests}, context_instance=RequestContext(request))

# Function to view recent notifications
def view_notifications(request):
    curr_uid = request.user.get_profile().facebook_id
    log_activity(curr_uid, 'view_notifications')
    res = Suggestion.objects.filter(target_user=curr_uid)
    notifications = []
    for curr_notify in res:
            curr_entry = {}
            if curr_notify.target_user is not None:
                curr_entry['target_user'] = UserProfile.objects.filter(facebook_id=int(curr_notify.target_user))[0].facebook_name
            if curr_notify.source_user is not None:
                curr_entry['source_user'] = FacebookUser.objects.filter(facebook_id=int(curr_notify.source_user))[0].name
            curr_entry['item_name'] =  FacebookFriendLike.objects.filter(facebook_id=int(curr_notify.item_id))[0].name
            notifications.append(curr_entry)
    return render_to_response('base/notifications.html', {'suggestions':notifications})    

def getMoreInfo(request):
    name = request.REQUEST['name']
    category = request.REQUEST['category']
    #itemfetcher = Itempedia(name, category)
    #item = itemfetcher.search_and_store()
    item_text = None
    item_subtitle = None
    if category == "MOVIE":
        response = urllib2.urlopen("http://api.rottentomatoes.com/api/public/v1.0/movies.json?q=%s&page_limit=1&page=1&apikey=bus3p2rf2fmkkx8pzd5ajucg" %urllib2.quote(name)) 
        item_resp = json.load(response)
        
        if item_resp['movies']:
            item_text = item_resp['movies'][0].get('critics_consensus')
            item_subtitle = item_resp['movies'][0].get('year')
    elif category == "MUSICIAN/BAND":
        response=urllib2.urlopen("http://ws.audioscrobbler.com/2.0/?method=artist.getinfo&artist=%s&api_key=14fed030365f7e6f85f2c426ffdaa56a&format=json" %urllib2.quote(name))
        item_resp = json.load(response)
        item_text = item_resp['artist']['bio']['summary']
        item_text = re.sub("\[[0-9]*\]",'',item_text)
        item_subtitle = None
        #return HttpResponse(item_text)
    elif category == "BOOK":
        response= urllib2.urlopen('https://www.googleapis.com/books/v1/volumes?q="%s"&key=AIzaSyCftB0ezz4wYGDgOwdE7ElUOOlPiOgJV7U' %(urllib2.quote(name)))
        item_resp = json.load(response)
        if 'items' in item_resp:
            for item in item_resp.get('items'):
                if item['volumeInfo']['title'].lower() == name.lower():
                    item_text = item['volumeInfo'].get('description')
                    item_subtitle = item['volumeInfo'].get('publishedDate')[:4]
                    break
            #return HttpResponse(item_resp['items'][0]['volumeInfo']['description'])
        
    return render_to_response('base/item_details.html',{'item_text':item_text, 'item_subtitle':item_subtitle, 'name':name, 'category':category}, context_instance=RequestContext(request))
