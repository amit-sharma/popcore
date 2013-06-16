from django.core.management.base import BaseCommand, CommandError
from django_facebook.models import FacebookFriendLike
from django_facebook.bulkops import insert_many

    
class Command(BaseCommand):
    args = '<poll_id poll_id ...>'
    help = 'Tests the db inserts performance'

    def handle(self, *args, **options):
        """f = FacebookFriendLike(user_id=10, friend_fid=5454,app_name='fo',
            facebook_id=4535,
            created_time='2011-10-24 11:40:52',
            release_date=None,
            category='fdfd',
            name='yoman',
            num_likes=5454,
            page_url='www.goel.com'
        )
        for i in xrange(10):
            flist =[f]*1000
        #for fr in flist:
        #    fr.save()
            insert_many(flist)
        self.stdout.write("Done")"""
        from greenlet import greenlet
        def test1():
            print 12
            gr2.switch()
            print 34

        def test2():
            print 56
            gr1.switch()
            print 78
        gr1 = greenlet(test1)
        gr2 = greenlet(test2)
        gr1.switch()



