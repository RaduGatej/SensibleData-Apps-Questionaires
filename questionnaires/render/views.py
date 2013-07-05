from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from utils import authorizations
from django.shortcuts import render_to_response
import formwidget

@login_required
def home(request):
	user = request.user
	auth = authorizations.getUserAuthorization(user)
	if auth == None:
		#show user site to authorize the form
		return render_to_response('start_auth.html', {'username': request.user.email})
	
	#TODO: check which questions has been answered already and do not include them
	return render_to_response('form.html', {'username': request.user.email})
	#return HttpResponse(formwidget.parsefile('/home/arks/MODIS/SensibleData-Apps-Questionaires/questionnaires/render/data/sample_new.txt')[0].render())
		
