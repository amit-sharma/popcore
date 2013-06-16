from django.http import HttpResponse
from django_facebook.api import get_facebook_graph
from threading import Thread

def myfunc(data):
    fid, graph,i = data
    fr_movies = graph.get("/" +fid+ "/movies") 
    print "Done",i
    #fr_movies['data']
    #print i, "Done"
    #i+= 1

def test_graphapi(request):
    graph = get_facebook_graph(request)
    friends = graph.get("/me/friends")
    friends = friends['data']
    flikes = {}
    i=0
    for fr in friends:
        fr_id = str(fr['id'])
        t = Thread(target=myfunc, args=((fr_id,graph,i),))
        t.start()
        i += 1
    return HttpResponse("Done")
