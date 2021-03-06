# Create your views here.
from django.http import HttpResponse
from django.template import loader, Context, RequestContext
from django.shortcuts import render_to_response, redirect
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django_facebook.decorators import facebook_login_required
from django_facebook.models import FacebookUser, FacebookLike
from django_facebook.api import get_facebook_graph
from open_facebook.api import FacebookConnection
from recommender.algorithms import RecConfig, RecOwnLikes, RecRandom, RecARM, RecQueue, RecFriendSim
from base.models import UserProfile, RuntimeFlags, ItemRating
from base.utils import log_activity
import json
import time 
RUNTIME_TASKBARRIER = 4
# TODO Include error handling for bad parameters
@csrf_exempt
@facebook_login_required
def content(request):
    print "Entering recommender.views.content"
    config = None
    BUFFER_MULTIPLIER = 4
    user=request.user.get_profile()
    max_items = int(request.REQUEST['maxitems'])
    algorithm = request.REQUEST['algorithm']
    postprocess_params = {}
    recency = request.REQUEST['recency']
    postprocess_params['popularity'] = int(request.REQUEST['popularity'])
    postprocess_params['close_friends'] = int(request.REQUEST['closefriends'])
    postprocess_params['trending'] = int(request.REQUEST['trending'])
    postprocess_params['acclaimed'] = int(request.REQUEST['acclaimed'])
    graph = get_facebook_graph(request)
    type_dict = {'movie_choose': 'MOVIE', 'music_choose': 'MUSICIAN/BAND', 'book_choose': 'BOOK'}
    freq = None
    item_category = None
    if algorithm == "queue":
        log_activity(user.facebook_id, 'view_queue')
    else:
        log_activity(user.facebook_id, 'view_recs')
    if 'category' in request.REQUEST:
        item_category = type_dict[request.REQUEST['category']]
    else:
        freq = {}
        try:
            freq['MOVIE'] = int(request.REQUEST['movieseq'])
            freq['TV SHOW'] = int(request.REQUEST['tvshowseq'])
            freq['BOOK'] = int(request.REQUEST['bookseq'])
            freq['MUSICIAN/BAND'] = int(request.REQUEST['musiceq'])
        except:
            #print "Error in converting parameters eq to integers"
            pass
    
    print freq
    
    flags = RuntimeFlags.objects.filter(user=request.user.id).filter(app_name=settings.POPCORE_APP_NAME)[0]
    tries = 0
    if flags.needs_update:
        while flags.tasks_barrier < RUNTIME_TASKBARRIER and tries <2:
            #print "waiting"
            time.sleep(3)
            flags = RuntimeFlags.objects.filter(user=request.user.id).filter(app_name=settings.POPCORE_APP_NAME)[0]
            tries += 1
        if flags.tasks_barrier < RUNTIME_TASKBARRIER:
            return HttpResponse("Processing your information from Facebook...")
    
        flags.needs_update = False
        flags.save()       
    
    config = RecConfig(max_items, item_category,BUFFER_MULTIPLIER, freq, recency,postprocess_params)
    if algorithm == "random":
        algo = RecFriendSim(request.user, graph, config, request.session)
    elif algorithm == "queue":
        algo = RecQueue(request.user, graph, config, request.session)
    
    algo.saveConfig()
    arr= algo.recommend()  
    arr = algo.postProcess()          
    #friends = FacebookUser.objects.filter(user_id=user.user_id)
    #likes = FacebookLike.objects.filter(user_id=user.user_tionid)
    d={'name':user.facebook_name, 'items':arr, 'algorithm': algorithm}
    return render_to_response("recommender/content.html", d, context_instance=RequestContext(request))
    #assert False, locals()
    
@csrf_exempt
def search(request):
    if 'query' in request.REQUEST:
        #graph = get_facebook_graph(request)
        kwargs = {'q': request.REQUEST['query'], 'type':'page'}
        search_results = FacebookConnection.request('search' ,**kwargs)
        
        #search_results=graph.get('search', **kwargs)
        item_list = search_results['data']
        filtered_list=[]
        for item in item_list:
            if item['category'] in ['Musician/band', 'Movie', 'Book', 'Tv show']:
                item['label'] = item['name']
                filtered_list.append(item) 
                
        #items = [{"label":'amitaaa', "category":"cat", 'desc':1000}, {"label":'amitiaaaa', "category": 'cat2', 'desc':1000}]
        return HttpResponse(json.dumps(filtered_list))
    return HttpResponse(None)    

@csrf_exempt
def showItem(request):
    try:
        fbid = request.REQUEST['id']
        name = request.REQUEST['name']
        category = request.REQUEST['category']
    except KeyError, e:
        return HttpResponse("Bad parameters")
    if request.user.is_authenticated():    
        log_activity(request.user.get_profile().facebook_id, 'search_item', name)    
    url = "http://www.facebook.com/profile.php?id=" + fbid;
    query_results = FacebookConnection.request(fbid)
    #query_results = graph.get(fbid)
    pic_url = None
    if 'cover' in query_results:
        pic_url = query_results['cover']['source']
    elif 'picture' in query_results:
        pic_url = query_results['picture']
        
    d = {'url': url, 'name':name, 'pic':pic_url, 'category':category, 'item_id':fbid}
    return render_to_response("recommender/showItem.html", d, context_instance=RequestContext(request));

def suggestPeople(request):
    user=request.user.get_profile()
    log_activity(user.facebook_id, 'click_suggest')
    friends = FacebookUser.objects.filter(user_id=user.user_id)
    import random
    #import time
    suggestedfr = random.sample(friends, 5)
    suggestedfr.append(FacebookUser(user_id=None, facebook_id=None, name="More..."))
    #time.sleep(5)
    return render_to_response("recommender/suggestPeople.html", {'friends': suggestedfr})
    
def storeItemRating(request):
    user=request.user.get_profile()
    itemid = request.REQUEST['item_id']
    rating = request.REQUEST['score']
    itemrating = ItemRating(source_user=user.facebook_id, item_id=itemid,rating=rating)
    itemrating.save()
    return HttpResponse("Stored item rating for item " + itemid)
