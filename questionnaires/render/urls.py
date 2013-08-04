from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	url(r'^nochanges','render.views.nochanges',name='changebrowser'),
    url(r'^form', 'render.views.form', name='form'),
    url(r'^about', 'render.views.about', name='about'),
    url(r'home_refreshed', 'render.views.home_refreshed', name='home_refreshed'),
    url(r'^', 'render.views.home', name='home'),
)
