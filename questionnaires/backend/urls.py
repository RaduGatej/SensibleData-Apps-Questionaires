from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
	url(r'^submit/', 'backend.input.submit'),
)
