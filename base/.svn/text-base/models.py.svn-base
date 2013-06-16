from django.db import models
from django_facebook.models import FacebookProfileModel
from django.contrib.auth.models import User
from django.conf import settings 

class BlobField(models.Field):
    description = "LongBlob"
    def db_type(self, connection):
        return 'longblob'
        
# Create your models here.
# Model for a user. Inherits from a FacebookProfileModel defined in djangoFacebook.
class UserProfile(FacebookProfileModel):
    '''
    Inherit the properties from django facebook
    '''
    user = models.OneToOneField(User)

# Model for a human-to-human suggestion
class Suggestion(models.Model):
    source_user = models.CharField(max_length=31)
    target_user = models.CharField(max_length=31)
    item_id = models.CharField(max_length=31)
    message = models.CharField(max_length=1023)
    isnew = models.BooleanField()
    created_time = models.DateTimeField(auto_now_add=True)
    app_name=models.CharField(max_length=7,default=settings.POPCORE_APP_NAME)

#Model for item rating
class ItemRating(models.Model):
    source_user = models.CharField(max_length=31)
    item_id = models.CharField(max_length=31)
    rating = models.FloatField()
    created_time = models.DateTimeField(auto_now_add=True)
    app_name=models.CharField(max_length=7,default=settings.POPCORE_APP_NAME)
    #unique_together = ('source_user','item_id')
    
# Model for an item in the queue of a user
class QueueItem(models.Model):
    source_user = models.CharField(max_length=31)
    item_type = models.CharField(max_length=31)
    item_id = models.CharField(max_length=31)
    item_link = models.TextField(null=True) 
    item_pic = models.TextField(null=True)
    item_name = models.TextField( null=True)
    created_time = models.DateTimeField(auto_now_add=True)
    app_name=models.CharField(max_length=7,default=settings.POPCORE_APP_NAME)

# Keeps the activities of a user on the server
class ActivityLog(models.Model):
    source_user = models.CharField(max_length=31)
    activity = models.CharField(max_length=31)
    data = models.CharField(max_length=63, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)
    app_name=models.CharField(max_length=7,default=settings.POPCORE_APP_NAME)

        
from django.db.models.signals import post_save
from django.dispatch import receiver

#These are to denote the runtime state of a user
class RuntimeFlags(models.Model):
    user = models.CharField(max_length=31, primary_key=True)
    tasks_barrier = models.SmallIntegerField()
    needs_update = models.BooleanField(default=True)
    app_name=models.CharField(max_length=7,default=settings.POPCORE_APP_NAME)
    class Meta:
        unique_together = (('user','app_name'),)

class UIConfig(models.Model):
    user = models.CharField(max_length=31, primary_key=True)
    movie_slider = models.SmallIntegerField(default=60)
    music_slider = models.SmallIntegerField(default=55)
    book_slider = models.SmallIntegerField(default=70)
    tv_slider = models.SmallIntegerField(default=30)
    popular_slider = models.SmallIntegerField(default=70)
    random_slider = models.SmallIntegerField(default=25)
    acclaim_slider = models.SmallIntegerField(default=50)
    closef_slider = models.SmallIntegerField(default=75)
    max_items = models.SmallIntegerField(default=20)
    recency = models.CharField(max_length=15, default="now")
    
class ItemRecommendations(models.Model):
    user = models.CharField(max_length=31, primary_key=True)
    recs_list = BlobField()
    update_time = models.DateTimeField(auto_now_add=True)
    
#helper function    
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """Create a matching profile whenever a user object is created."""
    if created: 
        profile, new = UserProfile.objects.get_or_create(user=instance)
