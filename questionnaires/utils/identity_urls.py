from django.conf.urls import patterns, include, url


urlpatterns = patterns('',
    url(r'^request_attributes/', 'utils.identity.requestAttributes', name='request_attributes'),
    url(r'^attributes_redirect/', 'utils.identity.attributesRedirect', name='attributes_redirect'),
    url(r'^test/', 'utils.identity.test'),
)
