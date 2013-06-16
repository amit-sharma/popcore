# Create your views here.
from django.http import HttpResponse
from django.template import loader, Context, RequestContext
from django.shortcuts import render_to_response, redirect
from django.views.decorators.csrf import csrf_exempt
from django_facebook.models import FacebookUser, FacebookLike
from django_facebook.api import get_facebook_graph
from django_facebook.decorators import facebook_login_required
from sandeep_test.models import HelloWorld
from pprint import pprint
#Definition for a view function. Redirected using urls.py
@csrf_exempt
#@facebook_login_required
def hello_world(request):
	user=request.user.get_profile()    
	graph = get_facebook_graph(request)
	type_dict = {'movie_choose': 'MOVIE', 'music_choose': 'MUSICIAN/BAND', 'book_choose': 'BOOK'}
#	arr = graph.fql("SELECT type, page_id, pic, page_url, name FROM page WHERE page_id IN (SELECT page_id FROM page_fan WHERE uid=me()) AND type IN ('{0}','{1}','{2}','{3}') LIMIT {4}".format('MOVIE','BOOK','TV SHOW','MUSICIAN/BAND',16*10))
	arr = graph.fql("SELECT uid, page_id FROM page_fan WHERE uid=me() AND type IN ('{0}','{1}','{2}','{3}') LIMIT {4}" \
		.format('MOVIE','BOOK','TV SHOW','MUSICIAN/BAND',16*10))

	pprint(arr)

	#returns the text to the client browser
	return HttpResponse("Some new text.");
