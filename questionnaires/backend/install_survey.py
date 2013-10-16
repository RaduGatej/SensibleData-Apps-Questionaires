from django_sensible import SECURE_CONFIG
import json
import urllib
from django.utils.http import urlquote
import urllib2
from django_sensible import settings
from render import formwidget
import hashlib
import xlrd
import csv
import os
from render.models import Survey


def install_survey(filename, title = '', prerequisite = ''):
	digest = hashlib.md5(open(filename).read()).hexdigest()
	widgets = formwidget.parse_file(filename)
	survey = []
	for q in widgets:
		survey.append(q.to_dict())

	data = json.dumps(survey)
	try:
		s = Survey.objects.get(form_version = digest)
		s.title = title
		s.content = data
		s.prerequiste = prerequisite
		s.save()
	except Survey.DoesNotExist:
		s = Survey(form_version = digest, title=title, content=data, prerequisite=prerequisite)
		s.save()
	
	
	#print doc
	#req = urllib2.Request(settings.SERVICE_INSTALL_URL)
	#data = {'data':json.dumps(doc)}
	#data = urllib.urlencode(data)
	#req.add_header('CONTENT_TYPE', 'application/json')
	#req.add_data(data)
	#print req.data
	#print urllib2.urlopen(req).read()
	
