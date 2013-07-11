from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import redirect
import SECURE_CONFIG

def do_logout(request):
	if request.user.is_authenticated():
		logout(request)
		return redirect(SECURE_CONFIG.IDP_URI+'accounts/logout/?next='+SECURE_CONFIG.APPLICATION_URI+'logout/')	
	return redirect('logout_success')	
