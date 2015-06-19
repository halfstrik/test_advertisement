from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import TemplateView

urlpatterns = patterns('',
                       url(r'^texts/', include('texts.urls', namespace='texts')),
                       url(r'^moderation/', include('moderation.urls', namespace='moderation')),
                       url(r'^audio_advertising/', include('audio_advertising.urls', namespace='audio_advertising')),
                       url(r'^auction/', include('auction.urls', namespace='auction')),
                       url(r'^admin/', include(admin.site.urls), name='admin'),
                       url(r'^$', TemplateView.as_view(template_name="test_advertisement/index.html"), name='index'),)
