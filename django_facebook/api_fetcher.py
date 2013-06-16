import urllib, json
from pprint import pprint
import MySQLdb
from time import sleep
#import reddit

#r = reddit.Reddit(user_agent='reddit_researcher')
#submissions = r.get_subreddit('politics').get_new(limit=None)
#list2=[str(x) for x in submissions]
#pprint(list2)
#submission = submissions.next()
#print submission.comments

SUBREDDIT = 'politics'
LIMIT=100
COLUMNS= "'approved_by', 'author', 'author_flair_css_class', 'author_flair_text', 'banned_by', 'clicked', 'created', 'created_utc', 'domain', 'downs', 'hidden', 'id', 'is_self', 'likes', 'media', 'media_embed', 'name', 'num_comments', 'num_reports', 'over_18', 'permalink', 'saved', 'score', 'selftext', 'selftext_html', 'subreddit', 'subreddit_id', 'thumbnail', 'title', 'ups'"

class AppURLopener(urllib.FancyURLopener):
    version = "reddit_researcher"

urllib._urlopener = AppURLopener()

db = MySQLdb.connect("localhost", "root", "pass", db="reddit")
c = db.cursor

after_fullname = 'None'

for i in range(0,2): 
    response = urllib.urlopen('http://www.reddit.com/r/{0}/new/.json?sort=new&limit={1}&after={2}'.format(SUBREDDIT, LIMIT, after_fullname))
    result = json.load(response)
    links = result['data']['children']
    for link in links:
        #print link['data']['name']
        query = u"INSERT INTO links ({0}) VALUES({1})".format(COLUMNS, COLSTRINGS)
         #VALUES({0})".format(','.join(map(unicode, link['data'].values())))
        print query
    after_fullname = result['data']['after']
    sleep(1)
