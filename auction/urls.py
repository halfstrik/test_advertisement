from django.conf.urls import patterns, url
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = patterns('',
                       url(r'^show_adv/$', 'auction.views.show_adv',
                           name='show_adv'),
                       ) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
