from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from utils import authorizations
from django.shortcuts import render_to_response

@login_required
def home(request):
	user = request.user
	auth = authorizations.getUserAuthorization(user)
	if auth == None:
		#show user site to authorize the form
		return render_to_response('start_auth.html', {})
	
	return render_to_response('form.html', {})
		
