from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from utils import oauth2, identity
from utils.models import Scope
from django.shortcuts import render_to_response, redirect
import formwidget
from django.template import RequestContext
import form_provider
import pdb

def home(request):
	return render_to_response('home.html', {}, context_instance=RequestContext(request))

@login_required
def form(request):
	#pdb.set_trace();
	#TODO add wrapper function for gettting authorizations
	#auth = oauth2.getToken(request.user, scope=Scope.objects.get(scope='connector_questionnaire.input_form_data'))
	#if auth == None:
		#show user site to authorize the form
	#	return render_to_response('start_auth.html', {}, context_instance=RequestContext(request))
	pdb.set_trace();
	# add answers:
	answers = [];
	required_vars = [];
	unanswered = False;
	for ans in request.POST.keys():
		if ans == 'required_vars': # list of required answers
			required_vars = request.POST[ans].split(",");
		elif ans == 'csrfmiddlewaretoken': # token
			continue
		elif request.POST[ans] == '': #empty answer
			unanswered = True;
		else: #good answer
			answers.append(ans);
			form_provider.set_answer(request.user, '1.0', ans, request.POST[ans]);
	if len(required_vars) > 0:
		for v in required_vars:
			if v not in answers:
				unanswered = True;
				break
		
	
	next_question = form_provider.get_next_unanswered_question(request.user,'1.0');
	if next_question is None:
		return render_to_response('form_last.html', {}, context_instance=RequestContext(request))
	
	di = {}
	di['question'] = form_provider.get_next_unanswered_question(request.user,'1.0').to_html()
	di['unanswered'] = unanswered
	pdb.set_trace()
	return render_to_response('form.html', di, context_instance=RequestContext(request))

@login_required
def login(request):
	getAttributes(request.user, ['email', 'first_name'])
	return redirect('home')

def logout_success(request):
	return render_to_response('logout_success.html', {}, context_instance=RequestContext(request))

def openid_failed(request):
	return render_to_response('openid_failed.html', {}, context_instance=RequestContext(request))
