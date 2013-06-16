from django.db import models
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
import django.dispatch
from django.conf import settings
class FacebookProfileModel(models.Model):
    '''
    Abstract class to add to your profile model.
    
    NOTE: If you don't use this this abstract class, make sure you copy/paste
    the fields in.
    '''
    about_me = models.TextField(blank=True)
    facebook_id = models.BigIntegerField(blank=True, unique=True, null=True)
    access_token = models.TextField(blank=True, help_text='Facebook token for offline access')
    facebook_name = models.CharField(max_length=255, blank=True)
    facebook_profile_url = models.TextField(blank=True)
    website_url = models.TextField(blank=True)
    blog_url = models.TextField(blank=True)
    image = models.ImageField(blank=True, null=True,
        upload_to='profile_images', max_length=255)
    date_of_birth = models.DateField(blank=True, null=True)
    raw_data = models.TextField(blank=True)
    app_name=models.CharField(max_length=7,default=settings.POPCORE_APP_NAME)
    
    def __unicode__(self):
        return self.user.__unicode__()
    
    class Meta:
        abstract = True
        
    def post_facebook_registration(self, request):
        '''
        Behaviour after registering with facebook
        '''
        from django_facebook.utils import next_redirect
        default_url = reverse('facebook_connect')
        response = next_redirect(request, default=default_url, next_key='register_next')
        response.set_cookie('fresh_registration', self.user_id)
        
        return response

class FacebookUser(models.Model):
    '''
    Model for storing a users friends
    '''
    #in order to be able to easily move these to a another db, use a user_id and no foreign key
    user_id = models.IntegerField()
    facebook_id = models.BigIntegerField()
    name = models.TextField(blank=True, null=True)
    tie_rank = models.IntegerField(default=0)
    app_name=models.CharField(max_length=7,default=settings.POPCORE_APP_NAME)

    class Meta:
        unique_together = ['user_id', 'facebook_id']

class FacebookLike(models.Model):
    '''
    Model for storing all of a users fb likes
    '''
    #in order to be able to easily move these to a another db, use a user_id and no foreign key
    user_id = models.IntegerField()
    facebook_id = models.BigIntegerField()
    name = models.TextField(blank=True, null=True)
    category = models.TextField(blank=True, null=True)
    created_time = models.DateTimeField(blank=True, null=True)
    release_date = models.DateTimeField(blank=True, null=True)
    pic = models.TextField(blank=True, null=True)
    page_url = models.TextField(blank=True, null=True)
    app_name=models.CharField(max_length=7,default=settings.POPCORE_APP_NAME)
    num_likes = models.BigIntegerField()
    
    class Meta:
        unique_together = ['user_id', 'facebook_id']

class FacebookFriendLike(models.Model):
    '''
    Model for storing all of a users friends' fb likes
    '''
    #in order to be able to easily move these to a another db, use a user_id and no foreign key
    user_id = models.IntegerField()
    friend_fid = models.BigIntegerField()
    facebook_id = models.BigIntegerField()
    name = models.TextField(blank=True, null=True)
    category = models.TextField(blank=True, null=True)
    created_time = models.DateTimeField(blank=True, null=True)
    release_date = models.DateTimeField(blank=True, null=True)
    pic = models.TextField(blank=True, null=True)
    page_url = models.TextField(blank=True, null=True)
    num_likes = models.BigIntegerField()
    app_name=models.CharField(max_length=7,default=settings.POPCORE_APP_NAME)
    
    class Meta:
        unique_together = ['friend_fid', 'facebook_id']
        

fbdata_processed = django.dispatch.Signal(providing_args=[])
