from django.conf.urls import patterns, url

urlpatterns = patterns('',
                       url(r'^add_text_couple/$', 'texts.views.add_text_couple', name='add_text_couple'), )
