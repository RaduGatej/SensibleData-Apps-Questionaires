from django.conf.urls import patterns, include, url


urlpatterns = patterns('',
    url(r'^authorize/', 'utils.oauth2.authorize', name='authorize'),
    url(r'^grant/', 'utils.oauth2.grant', name='grant'),
)
