from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^openid/', include('django_openid_auth.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^oauth2/', include('utils.oauth2_urls')),
    url(r'^identity/', include('utils.identity_urls')),
    url(r'^backend/', include('backend.urls')),
    url(r'^logout/', 'utils.logout.do_logout', name = 'logout'),
    url(r'^login/', 'utils.login.do_login', name = 'login'),
    url(r'^', include('render.urls')),
)
