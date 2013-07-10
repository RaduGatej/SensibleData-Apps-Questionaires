from render.models import Response
from utils import SECURE_CONFIG
import json
import urllib
from utils import oauth2
from utils.models import Scope
from django.core.urlresolvers import reverse

def sync_with_study():
	for response in Response.objects.filter(synced_with_study=False):
		values = {}
		values['form_version'] = str(response.form_version)
		values['variable_name'] = str(response.variable_name)
		values['response'] = str(response.response)
		values['last_answered'] = str(response.last_answered)

		values = urllib.quote(json.dumps(values))

		token = oauth2.getToken(response.user, Scope.objects.get(scope='connector_questionnaire.input_form_data'))
		print token
		response = oauth2.query('http://166.78.249.214:8082/connectors/connector_questionnaire/upload/', token, '&doc='+values, SECURE_CONFIG.CLIENT_ID, SECURE_CONFIG.CLIENT_SECRET, SECURE_CONFIG.APPLICATION_URI[:-1]+reverse('grant'), 'http://166.78.249.214:8082/connectors/connector_questionnaire/auth/refresh_token/')
		print response
