from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('mevlana_test',
    url(r'^hello/', 'views.hello_world', name='hello'),
)
