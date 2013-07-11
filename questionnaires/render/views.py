from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from utils import oauth2, identity
from utils.models import Scope
from django.shortcuts import render_to_response, redirect
import formwidget
from django.template import RequestContext
import form_provider

def home(request):
	return render_to_response('home.html', {}, context_instance=RequestContext(request))

@login_required
def form(request):
	#TODO add wrapper function for gettting authorizations
	#auth = oauth2.getToken(request.user, scope=Scope.objects.get(scope='connector_questionnaire.input_form_data'))
	#if auth == None:
		#show user site to authorize the form
	#	return render_to_response('start_auth.html', {}, context_instance=RequestContext(request))
	next_question = None;
	unanswered = False;
	if request.POST:
		if '_prev' in request.POST:
			next_question = form_provider.get_previous_question(request.user,'1.0',request.POST['__question_name']);
		elif '_from_top' in request.POST:
			next_question = form_provider.get_first_question(request.user,'1.0');
		else:
			# add answers:
			answers = [];
			required_vars = [];
			for ans in request.POST.keys():
				if ans == '__required_vars': # list of required answers
					required_vars = request.POST[ans].split(",");
				elif (ans == str('csrfmiddlewaretoken')) | (ans == str('__question_name')): # token or question_name
					continue
				elif request.POST[ans] == '': #empty answer
					continue
				else: #good answer
					answers.append(ans);
					form_provider.set_answer(request.user, '1.0', ans, request.POST[ans]);
			if len(required_vars) > 0:
				for v in required_vars:
					if v not in answers:
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
	if next_question is None:
		di['unanswered'] = False;
		di['last_page'] = True;
	else:	
		di['question'] = next_question.to_html()
		di['unanswered'] = unanswered
	return render_to_response('form.html', di, context_instance=RequestContext(request))

def logout_success(request):
	return render_to_response('logout_success.html', {}, context_instance=RequestContext(request))

def openid_failed(request):
	return render_to_response('openid_failed.html', {}, context_instance=RequestContext(request))
