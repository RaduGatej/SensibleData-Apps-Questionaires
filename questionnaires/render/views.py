from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from utils import authorizations
from django.shortcuts import render_to_response, redirect
import formwidget
from django.template import RequestContext

def home(request):
	return render_to_response('home.html', {}, context_instance=RequestContext(request))

@login_required
def form(request):
	auth = authorizations.getUserAuthorization(request.user)
	if auth == None:
		#show user site to authorize the form
		return render_to_response('start_auth.html', {}, context_instance=RequestContext(request))
	return render_to_response('form.html', {}, context_instance=RequestContext(request))

@login_required
def login(request):
	return redirect('home')

def logout_success(request):
	return render_to_response('logout_success.html', {}, context_instance=RequestContext(request))
