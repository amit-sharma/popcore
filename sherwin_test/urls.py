from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('sherwin_test',
    url(r'^content/', 'views.content', name='content'),
    url(r'^search/$', 'views.search', name='search'),
    url(r'^showItem/$', 'views.showItem', name='showItem'),
    url(r'^suggestPeople/$', 'views.suggestPeople', name='suggestPeople'),
    url(r'^calcTieStrength/$', 'tiestrength.calcTieStrength', name='calcTieStrength'),
    url(r'^storeItemRating/$', 'views.storeItemRating', name='storeItemRating'),
    # Examples:
    # url(r'^$', 'popcore.views.home', name='home'),
    # url(r'^popcore/', include('popcore.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
