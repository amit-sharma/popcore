from django_facebook.api import get_facebook_graph
from django.http import HttpResponse
from django.db import transaction
from pprint import pformat,pprint
import operator
from open_facebook.utils import json
from django_facebook.models import FacebookUser
"""
Tie Strength Signals:
1. Mutual Friends
2. Who (likes or )comments on a user status, post--consider only comments--they have more information, any one can like
2.1 whose posts the user comments
3. Who tags a user in anything (strong)
4. Who the user tags (very strong)
5. album, photo
6. friendlist

So using from GRAPH API: statuses, tagged, posts, mutualfriends
"""
#not necessarily friends
#@transaction.commit_manually
def calcTieStrength(user_fbid, user_id, graph):
    #user_fbid = request.user.get_profile().facebook_id
    #graph = get_facebook_graph(request)
    user_freq = analyzeUserFeed(user_fbid, graph)
    """friend_score = findMutualFriends(user_fbid, graph)
    tag_score = findTaggedFriends(user_fbid, graph)
    post_score = findWallPostsbyFriends(user_fbid, graph)
    total_score = {}
    friend_set = set(friend_score.keys() + post_score.keys() + tag_score.keys())
    for fr_id in friend_set:
        total_score[fr_id] = 0
        if fr_id in friend_score:
            total_score[fr_id] += friend_score[fr_id]
        if fr_id in tag_score:
            total_score[fr_id] += tag_score[fr_id]
        if fr_id in post_score:
            total_score[fr_id] += post_score[fr_id]"""
    close_frlist = sorted(user_freq.iteritems(), key=operator.itemgetter(1), reverse=True)
    rank = 1
    for key, score in close_frlist:
        fr_row = FacebookUser.objects.filter(user_id=user_id).filter(facebook_id=key).all()[0]
        print "Friend id",fr_row.facebook_id
        fr_row.tie_rank = rank
        fr_row.save()
        rank += 1
    
    #transaction.commit()
    #TODO check if all returned people are friends of the user        
    return close_frlist

#from http://stackoverflow.com/questions/4281210/facebook-mutual-friends-and-fql-4999-5000-record-limit    
def findMutualFriends(user_fbid, graph):
    friend_score = {}
    #count = 0   
    for i in range(1,10):
        
        fb_response = graph.fql("SELECT uid1,uid2 FROM friend WHERE uid1 IN (SELECT uid2 FROM friend WHERE uid1=me() AND strpos(uid2,{0})=6) AND uid2 IN (SELECT uid2 FROM friend WHERE uid1=me())".format(i))
        friends_arr = fb_response["data"]
    
        for pair in friends_arr:
            #count += 1
            uid1 = pair['uid1']
            if uid1 in friend_score:
                friend_score[uid1] += 1
            else:
                friend_score[uid1] = 1
        #print count          
    
    #removing all people with interaction==1. That does not convey much.
    for k,v in friend_score.items():
        if v<=1:
            del friend_score[k] 
    return friend_score


def analyzeUserFeed(user_fbid, graph):
    fqlstr = '{"query1": "SELECT post_id, actor_id, target_id, tagged_ids FROM stream WHERE source_id=%s AND app_id=\'\' LIMIT 100", "query2": "SELECT fromid from comment WHERE post_id IN (SELECT post_id FROM #query1)"}' %(user_fbid)
    fb_response = graph.fql(fqlstr)
    wall_updates = fb_response['data'][0]['fql_result_set']
    comments = fb_response['data'][1]['fql_result_set']
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
"""
def analyzeUserFeed(user_fbid, graph):
    batchstr = '[{"method":"GET","name":"getfeed","relative_url":"%s/feed?limit=50"},{"method":"GET","relative_url":"?ids={result=getfeed:$.data.*.id}"}]' %(user_fbid)
    postdata={'batch':batchstr}
    user_freq={}
    fb_response= graph.request(post_data=postdata)
    fb_updates_str =fb_response[1]['body']
    print fb_updates_str
    fb_updates = json.loads(fb_updates_str)
    for update_id, update in fb_updates.iteritems():
        if not ('status_type' in update and update['status_type'] == "approved_friend"):
            if not ('application' in update and update['application']['name'] == "likes"):
t                if 'story_tags' in update:
                    for key, user_obj in update['story_tags'].iteritems():
                        for u in user_obj:
                            tagged_id = u['id']
                            if tagged_id == str(user_fbid):
                                continue
                            if tagged_id in user_freq:
                                user_freq[tagged_id] += 1
                            else:
                                user_freq[tagged_id] = 1       
       
                if 'comments' in update and 'data' in update['comments']:
                    comments_arr = update['comments']['data']
                    for comm in comments_arr:
                        commenter_id = comm['from']['id']
                        #TODO:debug
                        if commenter_id == str(user_fbid):
                            continue
                            
                        if commenter_id in user_freq:
                            user_freq[commenter_id] += 1
                        else:
                            user_freq[commenter_id] = 1
    #print "user freq",user_freq
    return user_freq
"""    
#figure out why not working    
def findTaggedFriends(user_fbid, graph):
    tagged_friends = graph.fql("SELECT post_id,target_id FROM stream_tag WHERE actor_id=me()")
    print tagged_friends
    tag_score = {}
    for post in tagged_friends['data']:
        target_id = post['target_id']
        if target_id in tag_score:
            tag_score[target_id] += 1
        else:
            tag_score[target_id] = 1
            
    tagged_user = graph.fql("SELECT post_id,actor_id FROM stream_tag WHERE target_id=me()")
    print tagged_user
    tag_score = {}
    for post in tagged_user['data']:
        actor_id = post['actor_id']
        if actor_id in tag_score:
            tag_score[actor_id] += 1
        else:
            tag_score[actor_id] = 1
    return tag_score

def findWallPostsbyFriends(user_fbid, graph):
    profile_posts = graph.fql("SELECT post_id, actor_id, target_id FROM stream WHERE filter_key = 'others' AND source_id = me()") 
    print profile_posts
    post_score = {}
    for post in profile_posts['data']:
        actor_id = post['actor_id']
        if actor_id in post_score:
            post_score[actor_id] += 1
        else:
            post_score[actor_id] = 1
    return post_score    
    # post by user on friends walls--does not work
    """friends_posts = graph.fql("SELECT post_id, source_id, actor_id, message FROM stream WHERE actor_id=me() AND post_id IN (SELECT post_id FROM stream WHERE source_id IN (SELECT target_id FROM connection WHERE source_id=me()))")
    print friends_posts
    for post in friends_posts['data']:
        pass"""
