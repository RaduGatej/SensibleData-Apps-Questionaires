from render.models import Response
from django_sensible import SECURE_CONFIG
import json
import urllib
from django_sensible import oauth2
from django_sensible.models import Scope
from django.core.urlresolvers import reverse
from django.conf import settings

def sync_with_study(subtle=False, user=None):
	if not user == None:
		no = len(Response.objects.filter(synced_with_study=False, user=user))
	else:
		no = len(Response.objects.filter(synced_with_study=False))
	i = 0
	success = 0
	if not user == None:
		all_responses = Response.objects.filter(synced_with_study=False, user=user)
	else:
		all_responses = Response.objects.filter(synced_with_study=False)
	
	for response in all_responses:
		values = {}
		values['form_version'] = str(response.form_version)
		values['variable_name'] = str(response.variable_name)
		values['response'] = str(response.response.encode('utf-8'))
		values['last_answered'] = str(response.last_answered)

		values = urllib.quote(json.dumps(values))

		token = oauth2.getToken(response.user, Scope.objects.get(scope='connector_questionnaire.input_form_data'))

		r = oauth2.query(settings.SERVICE_UPLOAD_URL, token, '&doc='+values, SECURE_CONFIG.CLIENT_ID, SECURE_CONFIG.CLIENT_SECRET, settings.APPLICATION_URL[:-1]+reverse('grant'), settings.SERVICE_REFRESH_TOKEN_URL)
		if 'ok' in r:
			response.synced_with_study = True
			response.save()
			success += 1

		i += 1
		if subtle and i == 1: break
	return (i, success)
