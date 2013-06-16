from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': '/home/ubuntu/django_projects/popcore/static/change_later'}),
    #(r'^base/', include('base.urls')),
    url(r'^home/$', 'base.views.home', name='home'),
    url(r'^$', 'base.views.landing', name='landing'),
    url(r'^realtime/notify', 'base.realtime.notify', name="notify"),
    url(r'^realtime/addSuggestion', 'base.realtime.addSuggestion', name="addSuggestion"),
    url(r'^realtime/addQueue', 'base.realtime.addtoQueue', name="addtoQueue"),
    url(r'^realtime/receive_fb_updates', 'base.realtime.receiveFBUpdates', name="receiveFBUpdates"),
    url(r'^realtime/setup_fb_updates', 'base.realtime.setupFBUpdates', name="setupFBUpdates"),
    url(r'^view_profile/$', 'base.views.view_profile', name='view_profile'),
    url(r'^view_notifications/$', 'base.views.view_notifications', name='view_notifications'),
    url(r'^test_graphapi/$', 'base.testcode.test_graphapi', name='test_graphapi'),
    (r'^recommender/', include('recommender.urls')),
    (r'^visualize/', include('visualizor.urls')),
    (r'^facebook/', include('django_facebook.urls')),
    (r'^sandeep_test/', include('sandeep_test.urls')),  
    (r'^sherwin_test/', include('sherwin_test.urls')),  
    (r'^mevlana_test/', include('mevlana_test.urls')),  
    (r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', {'url': '/static/favicon.ico'}),
    url(r'^util/imageshack$', 'base.views.get_imageshack', name='get_imageshack' ),
    url(r'^util/get_more_info$', 'base.views.getMoreInfo', name='getMoreInfo' ),
    (r'', include('django.contrib.auth.urls')),
    (r'', include('django_socketio.urls')),
    # Examples:
    # url(r'^$', 'popcore.views.home', name='home'),
    # url(r'^popcore/', include('popcore.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
