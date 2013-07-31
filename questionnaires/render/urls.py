from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    url(r'^openid_failed', 'render.views.openid_failed', name='openid_failed'),
    url(r'^logout_success', 'render.views.logout_success', name='logout_success'),
    url(r'^form', 'render.views.form', name='form'),
    url(r'^about', 'render.views.about', name='about'),
    url(r'^quit', 'render.views.quit', name='quit'),
    url(r'home_refreshed', 'render.views.home_refreshed', name='home_refreshed'),
    url(r'^', 'render.views.home', name='home'),
)
