from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django_sensible import oauth2, identity
from django_sensible.models import Scope, FirstLogin
from render.models import Response, Survey
from django.shortcuts import render_to_response, redirect
import formwidget
from django.template import RequestContext
import form_provider
from backend.sync_with_study import *
import django_sensible
import pdb
import math
from django.conf import settings
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
import json
from datetime import datetime
import re

def home_refreshed(request):
	return render_to_response('home.html', {}, context_instance=RequestContext(request))

def home_platform(request):
	return HttpResponseRedirect(settings.IDP_URL)

def home(request):
	if settings.DO_AUTH:
		try:
			sessions = Session.objects.filter(expire_date__gte=datetime.now())
			for session in sessions:
				data = session.get_decoded()
				try: user = User.objects.filter(id=data.get('_auth_user_id', None))[0]
				except: continue
				if request.user == user:
					session.delete()
		except: pass

	if request.user.is_authenticated():
		try: f = FirstLogin.objects.get(user=request.user)
		except FirstLogin.DoesNotExist: f = FirstLogin.objects.create(user=request.user)
		if f.firstLogin:
			f.firstLogin = False
			f.save()
			#return redirect('request_attributes')
		identity.getAttributes(request.user, ['first_name'])

	
	if 'type_id' in request.GET.keys():
		postpone = '?type_id=' + request.GET.get('type_id')
	else: # redirected from login
		try: 
			postpone = '?type_id=' + request.META['HTTP_REFERER'].split('type_id%3D')[1]
		except:
			return HttpResponseRedirect(settings.ROOT_URL+'uselink/');
	return redirect(settings.ROOT_URL+'form/' + postpone)


@login_required
def form(request):
	#pdb.set_trace()
	if 'type_id' in request.GET.keys():
		request.session['type_id'] = request.GET.get('type_id')
	if settings.DO_AUTH:
		auth = oauth2.getToken(request.user, 'connector_questionnaire.input_form_data')
		if auth == None:
			#show user site to authorize the form
			status = request.GET.get('status', '')
			message = request.GET.get('message', '')
			return render_to_response('sensible/start_auth.html', {'status': status, 'message': message}, context_instance=RequestContext(request))
	survey_version = ''
	if request.POST: survey_version = request.POST.get('__survey_version','')
	try:
		Response.objects.get(user = request.user, type_id = request.session.get('type_id'), form_version=survey_version, variable_name='_submitted')
		return HttpResponseRedirect(settings.ROOT_URL+'nochanges/');
	except Exception:
		pass
	 
	next_question = None;
	unanswered = False;
	if request.POST:
		#pdb.set_trace()
		# add answers:
		answers = {};
		required_vars = [];
		for ans in request.POST.keys():
			if ans == '__survey_version': pass
			elif ans == '__required_vars': # list of required answers
				required_vars = request.POST[ans].split(",");
			elif (ans == str('csrfmiddlewaretoken')) | (ans == str('__question_name')): # token or question_name
				continue
			elif request.POST[ans] == '': #empty answer
				continue
			else: #good answer
				#pdb.set_trace();
				if ans.endswith('[]'):
					#pdb.set_trace()
					if len(request.POST.getlist(ans)) < int(float(request.POST['__required_answer_count'])):
						unanswered = True;
					answers[ans] = {'answer':','.join(request.POST.getlist(ans))}
					
				else:
					if not ans.startswith('_'):
						answers[ans] = {'answer':request.POST[ans]}
				#form_provider.set_answer(request.user, '1.0', ans, request.POST[ans]);
		set_answers(answers, request.user, request.session.get('type_id'), survey_version)
		if '_skip' in request.POST:
			next_question = form_provider.get_next_question(request.user,request.session.get('type_id'),survey_version,request.POST['__question_name'],skipping=True);
		else:
			
			if '_prev' in request.POST:
				next_question = form_provider.get_previous_question(request.user,request.session.get('type_id'), survey_version,request.POST['__question_name']);
			elif '_from_top' in request.POST:
				next_question = form_provider.get_first_question(request.user,request.session.get('type_id'), survey_version);
			elif '_quit' in request.POST:
				r = Response(user = request.user,type_id = request.session.get('type_id'), form_version=survey_version,variable_name='_submitted',response='true');
				r.save()
				return nochanges(request)
				#return HttpResponseRedirect(settings.SENSIBLE_URL+'quit/');
			else:
				if len(required_vars) > 0:
					for v in required_vars:
						if v not in answers.keys():
							unanswered = True;
							break
					
				if '_next' in request.POST:
					next_question = form_provider.get_next_question(request.user,request.session.get('type_id'),survey_version,request.POST['__question_name']);
				elif '_next_new' in request.POST:
					next_question = form_provider.get_next_unanswered_question(request.user,request.session.get('type_id'),survey_version);	
	else:
		survey_version = form_provider.get_survey_version(request.user,request.session.get('type_id'))
		if survey_version is not None:
			next_question = form_provider.get_next_question_from_timestamp(request.user,request.session.get('type_id'),survey_version)
		else:
			return HttpResponseRedirect(settings.ROOT_URL+'nochanges/')		

	di = {}
	di["type_id"] = request.session.get('type_id')
	progress = form_provider.get_user_progress(request.user,request.session.get('type_id'),survey_version);
	di['progress'] = str(progress);
	di['survey_version'] = survey_version
	progress = int(math.ceil(progress));
	
	di['int_progress'] = '' # accomodating Patrick's request to not show the percentage
	# if progress < 3:
	# 	di['int_progress'] = '';
	# elif progress < 7:
	# 	di['int_progress'] = str(int(progress)) + '%';
	# else: 
	# 	di['int_progress'] = 'ca. ' + str(int(progress)) + '%';
	try:
		di['required'] = next_question.required
	except: 
		di['required'] = True
	if next_question is None:
		di['unanswered'] = False;
		di['last_page'] = True;
	else:	
		di['question'] = next_question.to_html()
		di['unanswered'] = unanswered
	
	#try: sync_with_study(subtle=True, user=request.user)
	#except: pass

	return render_to_response('form.html', di, context_instance=RequestContext(request))



# answers_dict = dict with variable_names as keys and answers in dicts
def get_human_values(answers_dict, survey_version):	
	s = Survey.objects.get(form_version=survey_version)
	survey = json.loads(s.content)
	variables = answers_dict.keys()
	#pdb.set_trace()
	for q in survey:
	
		if 'data' in q.keys() and len(q['data']) > 0:
			for subq in q['data']:
				if subq['variable_name'] in variables:
					#pdb.set_trace()
					answer = None
					human_question = q['primary_content'] + '\n' + q['secondary_content'] + '\n' + q['additional_content'] + '\n' + subq['primary_content'] + '\n' + subq['secondary_content'] + '\n' + subq['additional_content']
					if 'number' or 'time' in subq['answer_type']:
						answer = answers_dict[subq['variable_name']]['answer']
					else:
						for a in subq['answers']:
							if a['htmlized'] == answers_dict[subq['variable_name']]['answer']:
								answer = a['raw']
					answers_dict[subq['variable_name']]['human_question'] = human_question
					if answer is None:
						answers_dict[subq['variable_name']]['human_answer'] = answers_dict[subq['variable_name']]['answer']
					else:
						answers_dict[subq['variable_name']]['human_answer'] = answer


		elif q['variable_name'] in variables:
			human_question = q['primary_content'] + '\n' + q['secondary_content'] + '\n' + q['additional_content']
			answer = None
			if 'header' in q['type'] or 'number' in q['answer_type']:
				answer = answers_dict[q['variable_name']]['answer']
			else:
				# if it is a list question, there can be multiple answers separated by commas
				parts = answers_dict[q['variable_name']]['answer'].split(',')
				if len(parts) > 0:
					answer = []
					for a in q['answers']:
						if a['htmlized'] in parts:
							answer.append(a['raw'])
				else:	
					for a in q['answers']:
						if a['htmlized'] == answers_dict[q['variable_name']]['answer']:
							answer = a['raw']
			answers_dict[q['variable_name']]['human_question'] = human_question
			if answer is None:
				answers_dict[q['variable_name']]['human_answer'] = answers_dict[q['variable_name']]['answer']
			elif type(answer) == list:
				answers_dict[q['variable_name']]['human_answer'] = ','.join(answer)
			else:
				answers_dict[q['variable_name']]['human_answer'] = answer
			break
	return answers_dict

def set_answers(answer_dict, user, type_id, survey_version):
	answer_dict = get_human_values(answer_dict, survey_version)
	for var in answer_dict.keys():
		o = answer_dict[var]
		form_provider.set_answer(user, type_id, survey_version, var, o['answer'], o['human_question'], o['human_answer'])

def nochanges(request):
	return render_to_response('nochanges.html', {'BASE_URL':settings.BASE_URL}, context_instance=RequestContext(request))

def uselink(request):
	return render_to_response('uselink.html', {'BASE_URL':settings.BASE_URL}, context_instance=RequestContext(request))
	
def about(request):
	return render_to_response('about.html', {}, context_instance=RequestContext(request))

