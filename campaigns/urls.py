from django.conf.urls import patterns, url,include
from django.conf.urls.static import static
from campaigns import views
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = patterns('',\

	
	url(r'^$',views.index, name='index'),
	url(r'^(?P<campaign_slug>[a-zA-Z0-9_.-]+)/$', views.campaign, name='campaign'),
	url(r'^(?P<campaign_slug>[a-zA-Z0-9_.-]+)/overview/$', views.overview, name='overview'),
	url(r'^(?P<campaign_slug>[a-zA-Z0-9_.-]+)/unsubscribe/(?P<subscriber_id>[0-9]+)/$',views.unsubscribe, name ='unsubscribe'),

	)

urlpatterns += staticfiles_urlpatterns()
