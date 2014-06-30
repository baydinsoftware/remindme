from django.conf.urls import patterns, url,include
from django.conf.urls.static import static
from campaigns import views
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth.decorators import login_required

urlpatterns = patterns('',\

	
	url(r'^$',views.index, name='index'),
	url(r'^(?P<campaign_slug>[a-zA-Z0-9_.-]+)/$', views.campaign, name='campaign'),
	url(r'^(?P<campaign_slug>[a-zA-Z0-9_.-]+)/overview/$', views.overview, name='overview'),
	url(r'^(?P<campaign_slug>[a-zA-Z0-9_.-]+)/unsubscribe/(?P<subscriber_id>[0-9]+)/(?P<subscriber_email_address>[a-zA-Z0-9_.-@]+)/$',views.unsubscribe, name ='unsubscribe'),
	url(r'^send_test/(?P<email_id>[0-9]+)/(?P<email_address>[a-zA-Z0-9_.-@]+)$',login_required(views.send_test)),
	url(r'send_test_addons/(?P<email_id>[0-9]+)/(?P<email_address>[a-zA-Z0-9_.-@]+)$',login_required(views.send_test_addons)),
)

urlpatterns += staticfiles_urlpatterns()
