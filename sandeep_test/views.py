# Create your views here.
from django.http import HttpResponse
from sandeep_test.models import HelloWorld

#Definition for a view function. Redirected using urls.py
def hello_world(request):
    #Creates a model object
    hw = HelloWorld(text="This is a test")
    #Saves the object to db
    hw.save()
    #returns the text to the client browser
    return HttpResponse(hw.text);
