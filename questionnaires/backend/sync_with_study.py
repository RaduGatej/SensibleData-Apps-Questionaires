from render.models import Response
from utils import SECURE_CONFIG
import json
import urllib
from utils import oauth2
from utils.models import Scope
from django.core.urlresolvers import reverse

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
		values['response'] = str(response.response)
		values['last_answered'] = str(response.last_answered)

		values = urllib.quote(json.dumps(values))

		token = oauth2.getToken(response.user, Scope.objects.get(scope='connector_questionnaire.input_form_data'))

		r = oauth2.query(SECURE_CONFIG.SERVICE_UPLOAD_URI, token, '&doc='+values, SECURE_CONFIG.CLIENT_ID, SECURE_CONFIG.CLIENT_SECRET, SECURE_CONFIG.APPLICATION_URI[:-1]+reverse('grant'), SECURE_CONFIG.SERVICE_REFRESH_TOKEN_URI)
		if 'ok' in r:
			response.synced_with_study = True
			response.save()
			success += 1

		i += 1
		if subtle and i == 1: break
	return (i, success)
