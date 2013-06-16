from base.models import ActivityLog

def log_activity(fbid, activity_str, data_str=None):
    if data_str:
        entry = ActivityLog(source_user=fbid, activity = activity_str, data=data_str)
    else:
        entry = ActivityLog(source_user=fbid, activity = activity_str)
    #print entry.activity
    entry.save()   
