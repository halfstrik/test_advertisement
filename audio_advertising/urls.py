from django.conf.urls import patterns, url
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = patterns('',
                       url(r'^add_audio_advertising/$', 'audio_advertising.views.add_audio_advertising',
                           name='add_audio_advertising'),
                       url(r'^list_audio_advertising/$', 'audio_advertising.views.list_audio_advertising',
                           name='list_audio_advertising'),
                       url(r'^view_audio_advertising/(?P<audio_advertising_id>\d+)/$',
                           'audio_advertising.views.view_audio_advertising',
                           name='view_audio_advertising'),
                       url(r'^delete_audio_advertising/(?P<audio_advertising_id>\d+)/$',
                           'audio_advertising.views.delete_audio_advertising',
                           name='delete_audio_advertising'),
                       url(r'^change_audio_advertising/(?P<audio_advertising_id>\d+)/$',
                           'audio_advertising.views.change_audio_advertising',
                           name='change_audio_advertising'),
                       ) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)