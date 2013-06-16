from celery import task
import logging
from django_facebook.utils import updateRuntimeFlags

logger = logging.getLogger(__name__)


@task.task(ignore_result=True)
def store_likes(user, likes):
    from django_facebook.api import FacebookUserConverter
    logger.info('celery is storing %s likes' % len(likes))
    FacebookUserConverter._store_likes(user, likes)
    return likes

@task.task(ignore_result=True)
def get_and_store_likes(user, facebook):

    '''
    Since facebook is quite slow this version also runs the get on the background
    '''
    stored_likes = facebook._get_and_store_likes(user)
    logger.info('celery is storing %s likes' % len(stored_likes))
    updateRuntimeFlags(user)
    print "fb stored likes for %s" % user.id
    
    return stored_likes

@task.task(ignore_result=True)
def store_friends(user, friends):
    from django_facebook.api import FacebookUserConverter
    logger.info('celery is storing %s friends' % len(friends))
    FacebookUserConverter._store_friends(user, friends)
    return friends

@task.task(ignore_result=True)
def get_and_store_friends(user, facebook):
    '''
    Since facebook is quite slow this version also runs the get on the background
    '''
    stored_friends = facebook._get_and_store_friends(user)
    logger.info('celery is storing %s friends' % len(stored_friends))
    updateRuntimeFlags(user)
    print "fb processing done: %s" % user.id
    return stored_friends

@task.task(ignore_result=True)
def get_and_store_friendlikes(user, facebook):
    '''
    Since facebook is quite slow this version also runs the get on the background
    '''
    stored_friends = facebook._get_and_store_friends(user)
    logger.info('celery is storing %s friends' % len(stored_friends))
    updateRuntimeFlags(user)
    print "fb stored friends for %s" % user.id
    
    #TODO function does not return anything, change later
    stored_friendlikes = facebook._get_and_store_friendlikes(user, stored_friends)
    #logger.info('celery is storing %s friendlikes' % len(stored_friendlikes))
    logger.info('celery is storing friendlikes')
    updateRuntimeFlags(user)
    print "fb stored friendlikes for user %s" % user.id
    return stored_friendlikes

@task.task(ignore_result=True)
def store_friendlikes(user, likes):
    pass

@task.task(ignore_result=True)
def get_and_store_tiestrength(user, facebook):
    close_frlist = facebook._get_and_store_tiestrength(user)
    logger.info('celery is storing %d tiestrength ranks' % len(close_frlist))
    print "fb stored tiestrength for user %s" % user.id
    updateRuntimeFlags(user)
    return close_frlist
    
@task.task()
def async_connect_user(request, graph):
    '''
    Runs the whole connect flow in the background.
    Saving your webservers from facebook fluctuations
    '''
    pass
    


