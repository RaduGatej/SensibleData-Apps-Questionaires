from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
import SECURE_CONFIG
from django.core.urlresolvers import reverse
from django.http import HttpResponse
import oauth2
import json
from .models import *
import urllib, urllib2

#TODO create common oauth2app method
@login_required
def requestAttributes(request):
	url = SECURE_CONFIG.IDP_AUTHORIZATION_URI
	url += "redirect_uri="+SECURE_CONFIG.BASE_URI[:-1]+reverse('attributes_redirect')
	url += "&client_id="+SECURE_CONFIG.IDP_CLIENT_ID
	url += "&response_type=code"
	url += "&scope="+','.join([s.scope for s in Scope.objects.filter(type=Type.objects.get(type='identity'))])
	state = oauth2.generateState(request.user)
	url += '&state='+state
	return redirect(url)
	#return HttpResponse(url)

@login_required
def attributesRedirect(request):
	token = oauth2.exchangeCodeForToken(request, SECURE_CONFIG.IDP_CLIENT_ID, SECURE_CONFIG.IDP_CLIENT_SECRET, SECURE_CONFIG.BASE_URI[:-1]+reverse('attributes_redirect'), SECURE_CONFIG.IDP_URI+'oauth2/oauth2/token/?')
	if 'error' in token:
		return HttpResponse(token)
	oauth2.saveToken(request.user, token)
	return redirect('home')

@login_required
def test(request):
	return HttpResponse(getAttributes(request.user, ['email', 'first_name']))


def getAttributes(user, attributes):
	tokens = set()
	for attribute in attributes:
		scope = (Attribute.objects.get(attribute=attribute).scope)
		token = oauth2.getToken(user, scope)
		tokens.add(token)
	if len(tokens) > 1: 
		return json.dumps({'error':'need multiple queries'})
	if len(tokens) == 0:
		return json.dumps({'error':'no token available'})
	
	response = oauth2.query(SECURE_CONFIG.IDP_URI + 'openid/attributes/', list(tokens)[0], '&attributes='+','.join(attributes), SECURE_CONFIG.IDP_CLIENT_ID, SECURE_CONFIG.IDP_CLIENT_SECRET, SECURE_CONFIG.BASE_URI[:-1]+reverse('attributes_redirect'), SECURE_CONFIG.IDP_URI+'oauth2/oauth2/token/?' )
	for attribute in response:
		s = 'user.'+attribute + '= response["%s"]'%attribute
		exec(s)
	user.save()
