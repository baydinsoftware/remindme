from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'remindme.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^admin/recursive_fixed','campaigns.admin_views.recursive_fixed'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^campaigns/',include('campaigns.urls',namespace="campaigns")),
    url(r'^tinymce/', include('tinymce.urls')), 
)

