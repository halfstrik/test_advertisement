from django.conf.urls import patterns, url
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = patterns('',
                       url(r'^send_to_moderation/(?P<advertising_id>\d+)/(?P<advertising_app>\w+)/'
                           r'(?P<advertising_model>\w+)/$',
                           'moderation.views.send_to_moderation',
                           name='send_to_moderation'),
                       url(r'^moderation/(?P<request_for_moderation_id>\d+)/$', 'moderation.views.moderation',
                           name='moderation'),
                       url(r'^list_request_for_moderation/$',
                           'moderation.views.list_request_for_moderation',
                           name='list_request_for_moderation'),
                       ) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
