from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
                       url(r'^texts/', include('texts.urls', namespace='texts')),
                       url(r'^moderation/', include('moderation.urls', namespace='moderation')),
                       url(r'^admin/', include(admin.site.urls), name='admin'), )
