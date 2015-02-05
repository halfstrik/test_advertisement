from django.conf.urls import patterns, url
urlpatterns = patterns('',
                       url(r'^$', 'texts.views.index', name='index'), )
