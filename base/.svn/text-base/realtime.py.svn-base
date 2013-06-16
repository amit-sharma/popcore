"""Contains functions for realtime applications


"""

from django.http import HttpResponse
from django.shortcuts import render_to_response
from base.models import Suggestion, UserProfile, QueueItem
from time import sleep
from django_facebook.api import get_facebook_graph
from django_facebook.models import FacebookFriendLike
from settings import FACEBOOK_APP_ID
from open_facebook.api import FacebookAuthorization
import urllib, random, string
import datetime

VERIFY_TOKEN = ''.join(random.choice(string.lowercase) for i in range(10))

# add support for friend likes about pages
def notify(request):
    updates = []
    notify_data = []
    try:
        curr_uid = request.user.get_profile().facebook_id
        newItemFound = False
        res=None
        res = Suggestion.objects.filter(target_user=curr_uid).filter(isnew=True)
        if res:
            newItemFound = True
            for sugg in res:
                sugg.isnew = False
                sugg.save()
        updates.extend(res)
        #allres = Suggestion.objects.filter(created_time__range=(datetime.datetime.today()-datetime.timedelta(hours=12),datetime.datetime.today()+datetime.timedelta(hours=12)))
        allres = Suggestion.objects.filter(created_time__range=(datetime.datetime.today()-datetime.timedelta(days=14),datetime.datetime.today()+datetime.timedelta(hours=12)))    
        if allres:
            for sugg in allres:
                if sugg.target_user!=curr_uid and sugg.source_user!=curr_uid:
                    sugg.target_user = None
                    sugg.source_user = None
                    updates.append(sugg)
            newItemFound = True
         
        for curr_update in updates:
            curr_entry = {}
            if curr_update.target_user is not None:
                curr_entry['target_user'] = UserProfile.objects.filter(facebook_id=int(curr_update.target_user))[0].facebook_name
            if curr_update.source_user is not None:
                curr_entry['source_user'] = UserProfile.objects.filter(facebook_id=int(curr_update.source_user))[0].facebook_name
            current_row =  FacebookFriendLike.objects.filter(facebook_id=int(curr_update.item_id))[0]
            curr_entry['item_name'] = current_row.name
            curr_entry['item_id'] = current_row.facebook_id
            curr_entry['category'] = current_row.category
            notify_data.append(curr_entry)
    #except ValueError:
    #    pass
    except:
        return HttpResponse("Some exception occured")    
    finally:
        pass
    
    return render_to_response('base/updates_ticker.html', {'suggestions':notify_data})    

"""
Add a suggestion when a user clicks to suggest

"""    
def addSuggestion(request):
    item = request.REQUEST['item_id']
    target = request.REQUEST['target']
    sharemessage = request.REQUEST['message']
    source = request.user.get_profile().facebook_id
    s = Suggestion(source_user= source, target_user=target, item_id=item, message=sharemessage, isnew=True)
    s.save()
    
    target_user = UserProfile.objects.filter(facebook_id=int(target))
    if not target_user:
        return HttpResponse("0")
    else:
        return HttpResponse(target_user)
"""
Add an item to the queue
"""

def addtoQueue(request):
    iid = request.REQUEST['item_id']     
    iname = request.REQUEST['item_name']
    ilink = request.REQUEST['item_link']        
    ipic = request.REQUEST['item_pic']        
    category = request.REQUEST['item_type']
    source = request.user.get_profile().facebook_id
    q = QueueItem(source_user = source, item_id = iid, item_name=iname, item_pic=ipic, item_link=ilink,item_type=category)
    q.save()
    return HttpResponse("1")

#TODO: log these changes and then when a user logs in, query only the items which happened AFTER than the last entry in table.
def receiveFBUpdates(request):
    if request.method == "GET" and request.GET['hub.mode'] == "subscribe" and request.GET['hub.verify_token'] == VERIFY_TOKEN:
        return HttpResponse(request.GET['hub.challenge'])
    elif request.method == "POST":
        updates = None
        return HttpResponse("Thanks")                    
    return HttpResponse(request.GET['hub.challenge'])                     
   
    #  $updates = json_decode(file_get_contents("php://input"), true); 
def setupFBUpdates(request):
    graph = get_facebook_graph(request)
    #get app's access token
    access_token = FacebookAuthorization.get_app_access_token()    
    params = {'access_token': access_token}
    postdata = {'object': 'user', 'fields': "friends,music,books,movies,tv,likes", 'callback_url':"http://www.popcore.me/realtime/receive_fb_updates", 'verify_token':VERIFY_TOKEN }
    url = '%s%s?%s' % ("https://graph.facebook.com/", FACEBOOK_APP_ID + "/subscriptions", urllib.urlencode(params))
    res= graph._request(url, post_data=postdata)
    #now check the new update configuration
   
    #import pprint
    response = graph._request(url)
    return HttpResponse(pprint.pformat(response))
#later, doing it manually right now

