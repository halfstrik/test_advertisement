from django.conf.urls import patterns, url

urlpatterns = patterns('',
                       url(r'^add_text_couple/$', 'texts.views.add_text_couple', name='add_text_couple'),
                       url(r'^list_text_couples/$', 'texts.views.list_text_couples', name='list_text_couples'),
                       url(r'^view_text_couple/(?P<text_couple_id>\d+)/$', 'texts.views.view_text_couple',
                           name='view_text_couple'),
                       url(r'^del_text_couple/(?P<text_couple_id>\d+)/$', 'texts.views.delete_text_couple',
                           name='del_text_couple'),
                       url(r'^change_text_couple/(?P<text_couple_id>\d+)/$', 'texts.views.change_text_couple',
                           name='change_text_couple'), )
