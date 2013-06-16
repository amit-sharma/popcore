# Create your views here.
from django.http import HttpResponse
from django.template import loader, Context, RequestContext
from django.shortcuts import render_to_response, redirect
from django.views.decorators.csrf import csrf_exempt
from django_facebook.models import FacebookUser, FacebookFriendLike
from random import shuffle
from django.db.models import Max, Count, Avg
from math import ceil
from datetime import datetime

@csrf_exempt
def tagcloud(request):
    from django.db import connection, transaction
    cursor = connection.cursor()
    d={}
    items=None
    if request.user.is_authenticated():
        user=request.user.get_profile()
        friends = FacebookUser.objects.filter(user_id=user.user_id)
        #items = FacebookFriendLike.objects.filter(user_id=user.user_id).values("facebook_id").annotate(num_likers=Count("friend_fid")).extra(select={'date_diff':"AVG(DATEDIFF(NOW(),'created_time'))"}).order_by("-num_likers").values('facebook_id', 'name', 'num_likers', 'date_diff')
        #items = FacebookFriendLike.objects.raw("SELECT facebook_id, name, COUNT(friend_fid) AS 'num_likers', AVG(DATEDIFF(NOW(), created_time)) AS 'avg_recency' FROM django_facebook_facebookfriendlike WHERE user_id= %s GROUP BY facebook_id ORDER BY num_likers DESC", [user.user_id])
        # Data retrieval operation - no commit required
        cursor.execute("SELECT facebook_id, name, category, COUNT(friend_fid) AS 'num_likers', AVG(DATEDIFF(NOW(), created_time)) AS 'avg_recency' FROM django_facebook_facebookfriendlike WHERE user_id= %s AND created_time is NOT NULL GROUP BY facebook_id ORDER BY num_likers DESC", [user.user_id])
        items = cursor.fetchall()
    else:
        cursor.execute("SELECT facebook_id, name, category, COUNT(user_id) AS 'num_likers', AVG(DATEDIFF(NOW(), created_time)) AS 'avg_recency' FROM django_facebook_facebooklike WHERE created_time is NOT NULL GROUP BY facebook_id ORDER BY num_likers DESC")
        items = cursor.fetchall()
        
        
    popularity=[]
    sizes=[]
    formatted_items=[]
    
    max_numlikers = items[0][3]
    max_timediff = 0
    for item in items:
        if item[4] > max_timediff:
            max_timediff = item[4]
    
    candidates = []
    for item in items:
        candidate = {}
        candidate['facebook_id'] = item[0]
        candidate['name'] = item[1]
        candidate['category'] = item[2]
        #print item[2], item[3]
        candidate['score'] = 4.0*float(item[3])/float(max_numlikers) + 6.0*float(item[4])/float(max_timediff)
        candidates.append(candidate)
    
    candidates.sort(key= lambda candi: candi['score'], reverse=True)
    show_size = min(10, len(items))
    candidates = candidates[0:show_size]
    i = show_size
    for candi in candidates:
        formatted_items.append({ 'size': "%d" % i, 'name': candi['name'], 'facebook_id': candi['facebook_id'],'category':candi['category'] })
        i -= 1
    if candidates:
        shuffle(formatted_items)  
        d={'formatted_items': formatted_items}

        
    return render_to_response("visualizor/tagcloud.html", d,context_instance=RequestContext(request))
    
