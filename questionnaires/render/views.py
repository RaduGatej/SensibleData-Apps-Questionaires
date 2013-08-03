from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from utils import oauth2, identity
from utils.models import Scope, FirstLogin
from render.models import Response
from django.shortcuts import render_to_response, redirect
import formwidget
from django.template import RequestContext
import form_provider
from backend.sync_with_study import *
import utils
import pdb
import math
from django.conf import settings
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
import json
from datetime import datetime

def home_refreshed(request):
	return render_to_response('home.html', {}, context_instance=RequestContext(request))

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
				return redirect('request_attributes')
			identity.getAttributes(request.user, ['email'])

	return redirect(settings.ROOT_URL+'form/')


@login_required
def form(request):
	if settings.DO_AUTH:
		auth = oauth2.getToken(request.user, 'connector_questionnaire.input_form_data')
		if auth == None:
			#show user site to authorize the form
			return render_to_response('start_auth.html', {}, context_instance=RequestContext(request))
	try:
		Response.objects.get(user = request.user,form_version='1.0',variable_name='_submitted')
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
			if ans == '__required_vars': # list of required answers
				required_vars = request.POST[ans].split(",");
			elif (ans == str('csrfmiddlewaretoken')) | (ans == str('__question_name')): # token or question_name
				continue
			elif request.POST[ans] == '': #empty answer
				continue
			else: #good answer
				#pdb.set_trace();
				if ans.endswith('[]'):
					#pdb.set_trace()
					if len(request.POST.getlist(ans)) < int(request.POST['__required_answer_count']):
						unanswered = True;
					answers[ans] = ','.join(request.POST.getlist(ans))
					
				else:
					if not ans.startswith('_'):
						answers[ans] = request.POST[ans];
				#form_provider.set_answer(request.user, '1.0', ans, request.POST[ans]);
		set_answers(answers, request.user, '1.0')
		if '_prev' in request.POST:
			next_question = form_provider.get_previous_question(request.user,'1.0',request.POST['__question_name']);
		elif '_from_top' in request.POST:
			next_question = form_provider.get_first_question(request.user,'1.0');
		elif '_quit' in request.POST:
			r = Response(user = request.user,form_version='1.0',variable_name='_submitted',response='true');
			r.save()
			return HttpResponseRedirect(settings.ROOT_URL+'quit/');
		else:
			if len(required_vars) > 0:
				for v in required_vars:
					if v not in answers.keys():
						unanswered = True;
						break
				
			if '_next' in request.POST:
				next_question = form_provider.get_next_question(request.user,'1.0',request.POST['__question_name']);
			elif '_next_new' in request.POST:
				next_question = form_provider.get_next_unanswered_question(request.user,'1.0');	
	else:
		next_question = form_provider.get_next_unanswered_question(request.user,'1.0');

	di = {}
	progress = form_provider.get_user_progress(request.user,'1.0');
	di['progress'] = str(progress);
	progress = int(math.ceil(progress));
	if progress < 3:
		di['int_progress'] = '';
	elif progress < 7:
		di['int_progress'] = str(int(progress)) + '%';
	else: 
		di['int_progress'] = 'ca. ' + str(int(progress)) + '%';
	if next_question is None:
		di['unanswered'] = False;
		di['last_page'] = True;
	else:	
		di['question'] = next_question.to_html()
		di['unanswered'] = unanswered
	
	try: sync_with_study(subtle=True, user=request.user)
	except: pass

	return render_to_response('form.html', di, context_instance=RequestContext(request))

def set_answers(answer_dict, user, survey_version):
	for var in answer_dict.keys():
		form_provider.set_answer(user, survey_version, var, answer_dict[var])

def changebrowser(request):
	return render_to_response('changebrowser.html', {}, context_instance=RequestContext(request))
	
def nochanges(request):
	return render_to_response('nochanges.html', {}, context_instance=RequestContext(request))
	
def noscript(request):
	return render_to_response('js_disabled.html', {}, context_instance=RequestContext(request))

def logout_success(request):
	return render_to_response('logout_success.html', {}, context_instance=RequestContext(request))

def openid_failed(request):
	return render_to_response('openid_failed.html', {}, context_instance=RequestContext(request))

def about(request):
	return render_to_response('about.html', {}, context_instance=RequestContext(request))

def quit(request):
		return redirect(utils.SECURE_CONFIG.SERVICE_URL+'quit')
