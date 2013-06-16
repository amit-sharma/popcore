from django_facebook.models import FacebookUser, FacebookFriendLike, FacebookLike
from base.models import QueueItem
from aggregates import Concatenate
from django.db.models import Count, Q
import operator
import heapq
import datetime
from pprint import pprint,pformat
from tiestrength import calcTieStrength
from random import random
"""Module containing logic for all recommendation algorithms
"""

"""Helper class that encapsulates common parameters for recommender
"""
class RecConfig:
    def __init__(self, max_items=10, item_category=False, buffer_mult=4, freq=None, recency=None, popularity=0,closefriends=0):
        self.MAX_ITEMS = max_items
        self.CATEGORY = item_category    
        self.BUFFER_MULTIPLIER = buffer_mult
        self.FREQ = freq
        self.RECENCY = recency
        self.POPULARITY = int(popularity)
        self.CLOSEFRIENDS = int(closefriends)

"""Base class for Recommender
"""        
class RecAlgo:
     def __init__(self, user, graph, config):
        self.targetUser = user.get_profile()
        self.targetUser_id = user.id
        self.config = config
        self.graph = graph
        self.arr = None
      
     def recommend(self):
        raise NotImplementedError("Please do")
     
     def postProcess(self):
        recency = self.config.RECENCY
        if recency == "old":
            self.arr.sort(key = lambda x: x['created_time'])
        if recency == "future":
            pass
        if self.config.CATEGORY:
            new_arr=[]
            for like in self.arr: 
                if like['type'] == self.config.CATEGORY:
                    new_arr.append(item)
            self.arr = new_arr[:self.config.MAX_ITEMS]
        elif self.config.FREQ:
            finish_count = 0
            #pprint(arr)
            new_arr = []
            freq = self.config.FREQ.copy()
            for item in self.arr:
                #print "Finish count",finish_count
                #pprint(item)
                if finish_count == len(freq):
                    break
                currCategory = item['type']
                if currCategory in freq:
                    if freq[currCategory] > 0:
                        new_arr.append(item)
                        #pprint(item)
                        freq[currCategory] -= 1
                        
                    if freq [currCategory] == 0:
                        finish_count += 1
                        freq[currCategory] = -1000
            self.arr = new_arr
        else:
            self.arr = self.arr[:self.config.MAX_ITEMS]
        return self.arr
        

"""Simple Recommender: Shows your own likes
"""
class RecOwnLikes (RecAlgo):
    def recommend(self):
        initial_arr = FacebookLike.objects.filter(user_id=self.targetUser.id)
        initial_arr = initial_arr[:min(len(initial_arr),self.config.MAX_ITEMS*self.config.BUFFER_MULTIPLIER*10)]
        arr=[]
        for like in initial_arr: 
            item = {}
            item['type'] = like.category
            item['page_id'] = like.facebook_id
            item['name'] = like.name
            item['pic']  = like.pic
            item['page_url'] = like.page_url
            item['created_time'] = like.created_time
            arr.append(item)
        """if self.config.CATEGORY:
            #fb_response = self.graph.fql("SELECT type, page_id, pic, page_url, name, release_date FROM page WHERE page_id IN (SELECT page_id FROM page_fan WHERE uid=me()) AND type='{0}' LIMIT 10".format(self.config.CATEGORY))
            #self.arr = fb_response['data']
            initial_arr = FacebookLike.objects.filter(user_id=self.targetUser.id)
            arr=[]
            for like in initial_arr: 
                item = {}
                item['type'] = like.category
                item['page_id'] = like.facebook_id
                item['name'] = like.name
                item['pic']  = like.pic
                item['page_url'] = like.page_url
                item['created_time'] = like.created_time
                arr.append(item)
            self.arr = arr[:min(len(arr),self.config.MAX_ITEMS*self.config.BUFFER_MULTIPLIER*10)]
        elif self.config.FREQ:
            #arr = self.graph.fql("SELECT type, page_id, pic, page_url, name, release_date FROM page WHERE page_id IN (SELECT page_id FROM page_fan WHERE uid=me()) AND type IN ('{0}','{1}','{2}','{3}') LIMIT {4}".format('MOVIE','BOOK','TV SHOW','MUSICIAN/BAND', self.config.MAX_ITEMS*self.config.BUFFER_MULTIPLIER*10))
            
            
            
            self.arr = arr
        else:
            arr = FacebookLike.objects.filter(user_id=self.targetUser.id)
            arr = arr[:self.config.MAX_ITEMS]
            self.arr = []
            for like in arr: 
                item = {}
                item['type'] = like.category
                item['page_id'] = like.facebook_id
                item['name'] = like.name
                item['pic']  = like.pic
                item['page_url'] = like.page_url
                item['created_time'] = like.created_time
                self.arr.append(item)
        
        """
        self.arr= arr
        return self.arr

"""Another simple recommender: Shows your own queue
"""
#TODO: why does queueitem object have no type!
class RecQueue(RecAlgo):
    def recommend(self):
        qitems = QueueItem.objects.filter(source_user =self.targetUser.facebook_id)
        self.arr = []
        for qi in qitems: 
            item = {}
            item['type'] = qi.item_type
            item['page_id'] = qi.item_id
            item['name'] = qi.item_name
            item['pic']  = qi.item_pic
            item['page_url']  = qi.item_link
            self.arr.append(item)
        return self.arr

"""Simple Recommender which shows random items from your friends
"""
#TODO: why does FacebookFriendLike object have no type!
class RecRandom(RecAlgo):
    def recommend(self):
        import random
        
        friend_rows = FacebookUser.objects.filter(user_id=self.targetUser.id)
        items = []
        for fr in friend_rows:
            items.extend(FacebookFriendLike.objects.filter(friend_fid=fr.facebook_id))
        selected = random.sample(xrange(len(items)), min(len(items),self.config.MAX_ITEMS*self.config.BUFFER_MULTIPLIER*10))
        self.arr = []
        for i in selected: 
            item = {}
            item['type'] = items[i].category
            item['page_id'] = items[i].facebook_id
            item['name'] = items[i].name
            item['pic']  = items[i].pic
            item['page_url'] = items[i].page_url
            item['created_time'] = items[i].created_time
            self.arr.append(item)
        #pprint(self.arr)
        return self.arr

class RecFriendSim(RecAlgo):
    def recommend(self):
        
        friend_rows = FacebookUser.objects.filter(user_id=self.targetUser.id)
        friend_idlist = [(fr.facebook_id,1) for fr in friend_rows]
        
        #close_frlist = calcTieStrength(self.targetUser.facebook_id, self.targetUser_id, self.graph)
        close_frlist = [(fr.facebook_id,fr.tie_rank) for fr in friend_rows if fr.tie_rank > 0]
        CLOSEFR_CUTOFF = (self.config.CLOSEFRIENDS)/100 
        print close_frlist
        #numInteractions_list=[cfr[1] for cfr in close_frlist]
        #print numInteractions_list
        cutoff_index = int(CLOSEFR_CUTOFF* len(close_frlist))-1
        closefriend_idlist = close_frlist[:cutoff_index]
        
        	
        friend_items =dict()
        if self.config.RECENCY == "now":
            SINCE_DAYS = 300
            TILL_DAYS = None
        elif self.config.RECENCY == "old":
            SINCE_DAYS = None
            TILL_DAYS = 300
        for fr_tuple in friend_idlist:
            if self.config.RECENCY == "now":
                friend_items[fr_tuple[0]] = FacebookFriendLike.objects.filter(friend_fid=fr_tuple[0]).filter(created_time__gt=(datetime.datetime.today()-datetime.timedelta(days=SINCE_DAYS)))
            elif self.config.RECENCY == "old":
                friend_items[fr_tuple[0]] = FacebookFriendLike.objects.filter(friend_fid=fr_tuple[0]).filter(created_time__lt=(datetime.datetime.today()-datetime.timedelta(days=TILL_DAYS)))    
        
        user_likes = FacebookLike.objects.filter(user_id=self.targetUser.id)
        
        self.targetUserLikes = dict()
        for item in user_likes:
            self.targetUserLikes[str(item.facebook_id)] = True
        friend_score = dict()
        for key, fr in friend_items.iteritems():
            score = 0
            for fitem in fr:
                if  str(fitem.facebook_id) in self.targetUserLikes:
                    score += 1
            if score > 0:
                friend_score[key] = score
        item_scores = {}
        all_items = {}

        item_weights = {}
        #only friends in cfr_idlist
        cfr_idlist = []
        for (fr_id, fr_closescore) in closefriend_idlist:
            if long(fr_id) in friend_items:
                cfr_idlist.append((long(fr_id),fr_closescore))
        for (fr_id, fr_closescore) in cfr_idlist:
            fr_list = friend_items[long(fr_id)]
            for fitem in fr_list:
                if fitem.facebook_id not in item_weights:
                    item_weights[fitem.facebook_id] = 0
                item_weights[fitem.facebook_id] += fr_closescore
        #pprint(item_weights)
        for key, fr in friend_items.iteritems():
            if key in friend_score:
                curr_fscore = friend_score[key]
            for fitem in fr:
                if key in friend_score:
                    if fitem.facebook_id not in item_scores:
                        item_scores[fitem.facebook_id] = 0
                        all_items[fitem.facebook_id] = fitem
                    item_scores[fitem.facebook_id] += curr_fscore
                if fitem.facebook_id in item_weights:
                    if fitem.facebook_id not in item_scores:
                        item_scores[fitem.facebook_id] = 0
                        all_items[fitem.facebook_id] = fitem 
                    #ranking dependent on relative weights of similar friends and close friends
                    item_scores[fitem.facebook_id] = random() * item_weights[fitem.facebook_id]
        #scores_list is a list of tuples(item_id, score)
        scores_list = sorted(item_scores.items(), key=lambda x: x[1], reverse=True) 
        #pprint(scores_list)  
        self.arr = []
        if len(scores_list) == 0:                   
            return self.arr
       
        
        TOP_CUTOFF = (100.0 - self.config.POPULARITY)/100 
        print TOP_CUTOFF
        """deficit = self.config.MAX_ITEMS - (1-TOP_CUTOFF)*len(scores_list)
        if self.config.CLOSEFRIENDS and deficit > 0:
            for (fr_id, close_score) in friend_idlist:
                
            for i in deficit:
                wrandom_itemid = weighted_random(weights)
                scores_list.append((wrandom_itemid,0))
        """
        numlikes_list = [all_items[item_tuple[0]].num_likes for item_tuple in scores_list]        
        #pprint(numlikes_list)
        if TOP_CUTOFF*len(numlikes_list)<1:
            cutoff_numlikes = max(numlikes_list)
        else:
            cutoff_numlikes = heapq.nlargest(int(TOP_CUTOFF* len(numlikes_list)), numlikes_list)[-1]
        print "Cutoff",cutoff_numlikes
        
        #Fix to remove items with duplicate names, and items already liked by the targetUser
        rec_names = {}
        for i in range(min(len(scores_list),self.config.MAX_ITEMS*self.config.BUFFER_MULTIPLIER*10)):
            item = {}
            rec_item = all_items[scores_list[i][0]]
            if rec_item.num_likes <= cutoff_numlikes and rec_item.name not in rec_names and str(rec_item.facebook_id) not in self.targetUserLikes:
                item['type'] = rec_item.category
                item['page_id'] = rec_item.facebook_id
                item['name'] = rec_item.name
                item['pic']  = rec_item.pic
                item['page_url'] = rec_item.page_url
                item['created_time'] = rec_item.created_time
                self.arr.append(item)
                rec_names[rec_item.name]=True
        return self.arr
        
"""Recommender using Association Rule Mining as per \cite{}
	Here each item corresponds to a transaction. If users like an item, then they are added to that item's transaction.
"""
class RecARM(RecAlgo):
    #Represents a candidate rule. A rule is a set of users(i.e.friends).
    class Candidate:
        condsupCount = 0
        rulesupCount = 0
        condset = None
        condlist = None
        def __init__(self, condset):
            self.condset = condset
            self.condlist = sorted(list(condset))
            
       	def __str__(self):
       		return str(self.condlist)
    
    #Represents an array of rules. An array of candidates, plus two variables for bookkeeping    
    class Rules:
        aboveMaxNumRulesFlag = None
        belowMinNumRulesFlag = None
        rules_list = None
        def __init__(self, rules_list, maxRules):
            self.rules_list = rules_list
            if len(self.rules_list) >  maxRules:
                self.aboveMaxNumRulesFlag = True
    
    #Main recommend function    
    def recommend(self):
        #Initialize
        self.minConfidence = 0.7
        self.minNumRules = 1
        self.maxNumRules = 100
        """get friend likes grouped by item, and user likes"""
        grouped_users = FacebookFriendLike.objects.filter(user_id=self.targetUser.id).values('facebook_id').annotate(Concatenate('friend_fid')).order_by('facebook_id')
        #print "LEngth:", len(grouped_users), self.targetUser.id
        """Get user likes"""
        user_likes = FacebookLike.objects.filter(user_id=self.targetUser.id)
        #pprint(grouped_users)
        
        # Creating a hashtable of transactions
        self.transactions = {}
        for item in grouped_users:
            self.transactions[str(item['facebook_id'])] = set(item['friend_fid__concatenate'].split(" / "))
        
        self.targetUserLikes = {}
        for item in user_likes:
            self.targetUserLikes[str(item.facebook_id)] = True
        """for item in user_likes:
            if str(item.facebook_id) in self.transactions:
                #print "Yes", item.facebook_id
                self.transactions[str(item.facebook_id)] |= set([str(self.targetUser.id)]) """
        #print self.transactions
        """Creating the list of users. (i.e. all friends who like an item that the target user has liked)"""
        self.user_list = []
        for key, users in self.transactions.iteritems():
        	if key in self.targetUserLikes:
		        for u in users:
		            if (u not in self.user_list):
		                self.user_list.append(u)
        
        #print len(self.user_list)             
        self.minSupportCount  = len(self.targetUserLikes)/10 -3
        #self.minSupportCount = 3
         #TODO make it variable
        
        #Main call to ARM 
        final_rules= self.asarm_outer()
        for fr in final_rules:
            print "rule: ", fr.condset
            
        #Recommendation step: calculate scores for items, sort and return    
        item_scores = self.calculateItemScores(final_rules)
        sorted_items = sorted(item_scores.iteritems(), key=operator.itemgetter(1), reverse=True)
        self.arr = self.getItemDetails(item_scores, self.config.MAX_ITEMS)
        #print "algorithms.py: Array is ",self.arr
        """
        """
        #self.arr = sorted_items[:10]
        #print "sorted items: ", sorted_items
        return self.arr
    
    # Repeatedly call asarm() until satisfied with the values
    def asarm_outer(self):
        r = self.asarm()
        
        while r.aboveMaxNumRulesFlag or r.belowMinNumRulesFlag:
            if r.aboveMaxNumRulesFlag:
                print "Above flag"
                if self.minSupportCount == len(self.transactions):
                    return r.rules_list
                print "Support Count is: ",self.minSupportCount
                self.minSupportCount += 1
                r1 = r
                r = self.asarm()
                if r.belowMinNumRulesFlag:
                    return self.combineRuleLists(r.rules_list,r1.rules_list) 
            else:
                print "Below flag"
                if self.minSupportCount == 0:
                    return r.rules_list
                print "Support Count is: ",self.minSupportCount
                self.minSupportCount -= 1
                
                r1 = r
                r = self.asarm()
                if r.aboveMaxNumRulesFlag:
                    return self.combineRuleLists(r.rules_list,r1.rules_list) 
        
        return r.rules_list
        
    def asarm(self):
        f = []
        f.append([])
        f_1, r = self.generateInitialRules()
        #print r
        f.append(f_1) #f[1]
        c = [[],[]]
        k = 2
        while len(f[k-1]) > 0 and not r.aboveMaxNumRulesFlag:
            print "k is", k
            c_k = self.candidateGenerate(f[k-1], k-1)
            c.append(c_k) #c[k] 
            print "Number of candis:",len(c_k)
            for key, users in self.transactions.iteritems():
                for candidate in c_k:
                    #print candidate.condset
                    if candidate.condset <= users:
                        candidate.condsupCount += 1
                        if key in self.targetUserLikes:
                            candidate.rulesupCount += 1
            
            print "Candidates found"
            frequent_candidates = []
            rules = []
            for candidate in c_k:
                if candidate.rulesupCount >= self.minSupportCount:
                    frequent_candidates.append(candidate)
                    candidate_confidence = (candidate.rulesupCount*1.0)/candidate.condsupCount
                    if candidate_confidence > self.minConfidence:
                        rules.append(candidate)  
            f_k = frequent_candidates                     
            f.append(frequent_candidates) #f[k]
            print "Frequent Candidates found"
            r1 = RecARM.Rules(rules, self.maxNumRules)
            if (len(r.rules_list) + len(r1.rules_list) > self.maxNumRules) or r1.aboveMaxNumRulesFlag:
                r.aboveMaxNumRulesFlag = True
            r.rules_list = self.combineRuleLists(r.rules_list,r1.rules_list)       
            
            k += 1
        if len(r.rules_list) < self.minNumRules:
            r.belowMinNumRulesFlag = True
        return r
        
        
    def generateInitialRules(self):
        c_1 = self.candidateGenerate(None,0)
        #print c_1[0].condset
        for key, users in self.transactions.iteritems():
            for candidate in c_1:
                if candidate.condset <= users:
                    #print candidate.condset, users
                    candidate.condsupCount += 1
                    if key in self.targetUserLikes:
                        candidate.rulesupCount += 1
        
        frequent_candidates = []
        rules = []
        for candidate in c_1:
            #print candidate.rulesupCount
            if candidate.rulesupCount >= self.minSupportCount:
                frequent_candidates.append(candidate)
                candidate_confidence = (candidate.rulesupCount*1.0)/candidate.condsupCount
                #print candidate_confidence
                if candidate_confidence > self.minConfidence:
                    rules.append(candidate)  
        f_1 = frequent_candidates
        #print f_1
        from pprint import pprint
        print len(rules)
        #for ru in rules:
        #    pprint(ru.condset)
        r = RecARM.Rules(rules, self.maxNumRules)                     
        return (f_1,r)  
        """sorted_users = sorted(support.iteritems(), key=operator.itemgetter(1))
        self.user_list = support.keys()
        frequent_users = []
        for user, supportCount in sorted_users
            if supportCount > self.minSupportCount:
                frequent_users.append(user)
        return frequent_users"""
        
    
    def candidateGenerate(self, f_i,i):
        candidates = []
        if f_i is None:
            for u in self.user_list:
                c_new = RecARM.Candidate(set([u]))
                candidates.append(c_new)
                #print c_new.condset
            return candidates
            
        condsets = []
        
        
        print "Size of f_i:",len(f_i)
        counter = 0
      	for a in range(0,len(f_i)-1):
      		for b in range(a+1,len(f_i)):
      			join_eligible = True
      			#TODO  optimize by reversing the order of if
      			#raise ValueError(str(f_i[0]))
      			for p in range(i-1):
      				if f_i[a].condlist[p] != f_i[b].condlist[p]:
      					join_eligible = False
      					break
      			if join_eligible and f_i[a].condlist[i-1] < f_i[b].condlist[i-1]:
  					new_condset = f_i[a].condset | set([f_i[b].condlist[i-1]])	
  					#if not self.pruneCondset(new_condset,f_i):
  					if True:
	  					c_new = RecARM.Candidate(new_condset)
	  					candidates.append(c_new)
	  					condsets.append(new_condset)
      			if counter % 1000 == 0:
      				print "Iteration: ",a,b				
      			counter += 1
         
        
        """
        #print "Entering"
        eligible_pool=set()
        for freq_set in f_i:
            eligible_pool |= freq_set.condset 
        #print eligible_pool, "Eligible"
        for prev_candidate in f_i:
            for user in eligible_pool:
                if user not in prev_candidate.condset:
                    new_condset = prev_candidate.condset | set([user])
                    #print new_condset            
                    if new_condset not in condsets:
                        c_new = RecARM.Candidate(new_condset)
                        candidates.append(c_new)
                        condsets.append(new_condset)
        """
        return candidates
                        #print c_new.condset
        """
        for key, users in self.transactions.iteritems():
            if prev_candidate.condset <= users:
                for u in users:
                    if u not in prev_candidate.condset:
                        new_condset = prev_candidate.condset | set([u])
                        #print new_condset            
                        if new_condset not in condsets:
                            c_new = RecARM.Candidate(new_condset)
                            candidates.append(c_new)
                            condsets.append(new_condset)
    
        for user in self.user_list:
            new_condset = prev_candidate.condset | set([user])
            print new_condset
            if new_condset not in condsets:
                c_new = RecARM.Candidate(new_condset)
                candidates.append(c_new)
                condsets.append(new_condset)"""
        #print "Candidates are ", candidates 
        
    
    """def generateRules(self, f1)
        confidence = {}
        for candidate_ruleuser in f1:
            for key, users in self.transactions.iteritems():
                if candidate_ruleuser in users and self.targetUser.id in users:
                    if candidate_ruleuser in confidence:
                        confidence[candidate_ruleuser] += 1
                    else:
                        confidence[candidate_ruleuser] = 1
        rules = {}
        i = 0
        for rule, confidence_value in confidence.iteritems():
            if confidence_value > self.minConfidence
                if i >= self.maxNumRules:
                    rules[rule]['aboveMaxRulesNumFlag'] = True
                    break
                rules[rule] = {}                
                rules[rule]['confidence'] = confidence_value
                i += 1 
                    
        return rules"""
    
    def pruneCondset(self,condset,freq_candidates):
    	freq_condsets_list=[]
    	for freq_c in freq_candidates:
    		freq_condsets_list.append(freq_c.condset)
    	prune = False
    	for u in condset:
    		testset = condset - set([u])
    		if testset not in freq_condsets_list:
    			prune = True
    			break
    	
    	return prune
    	
    def calculateItemScores(self, rules_list):
        item_scores = {}
        for key, users in self.transactions.iteritems():
            if key not in self.targetUserLikes:
                for rule in rules_list:
                    if rule.condset <= users: # rule has fired
                        rule_support = rule.rulesupCount
                        rule_confidence = (rule.rulesupCount*1.0)/rule.condsupCount
                        if key in item_scores:
                            item_scores[key] += (rule_support *rule_confidence)
                        else:
                            item_scores[key] = (rule_support *rule_confidence)
        return item_scores
    
    def combineRuleLists(self, rlist1, rlist2):
        rlist1.extend(rlist2) 
        rlist1.sort(key= lambda x: x.rulesupCount, reverse=True)
        listlength = self.maxNumRules if self.maxNumRules <= len(rlist1) else len(rlist1)
        return rlist1[:listlength]
    
    def getItemDetails (self, item_scores, max_items): 
        queries = [Q(facebook_id=item_id) for item_id in item_scores.keys()]
        itemarr = []
        if len(queries) >0:
            query = queries.pop()
            for currq in queries:
                query |= currq
        
            items = FacebookFriendLike.objects.filter(query).values('facebook_id').annotate(Count('friend_fid')).values('facebook_id', 'category','name', 'pic','page_url')
        #print items
        
            for i in range(len(items)): 
                item = {}
                item['type'] = items[i]['category']
                item['page_id'] = items[i]['facebook_id']
                item['name'] = items[i]['name']
                item['page_url'] = items[i]['page_url']
                itemarr.append(item)
        return itemarr
        
