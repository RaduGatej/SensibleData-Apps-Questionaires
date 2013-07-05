from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import uuid
import hashlib
from .models import *
from utils import SECURE_CONFIG
from django.shortcuts import redirect


@login_required
def authorize(request):
	state = generateState(request.user)
	url = SECURE_CONFIG.SERVICE_URL + SECURE_CONFIG.AUTH_ENDPOINT + SECURE_CONFIG.CONNECTOR
	url += '/auth/grant/?'
	#TODO: this support just single scope
	scope = Scope.objects.get().scope
	url += 'scope='+scope
	url += '&client_id='+SECURE_CONFIG.CLIENT_ID
	url += '&state='+state
	return redirect(url)


def generateState(user):
	return State.objects.create(user=user).nonce


@login_required
def grant(request):
	state = request.REQUEST.get('state', '')
	access_token = request.REQUEST.get('access_token', '')
	scope = request.REQUEST.get('scope', '')
	token_type = request.REQUEST.get('token_type', '')
	expires_in = request.REQUEST.get('expires_in', '')
	refresh_token = request.REQUEST.get('refresh_token', '')

	if saveToken(request.user, state, access_token, scope, refresh_token):
		return redirect('home')
	else:
		#TODO push to auth_error
		return redirect('home')



def saveToken(user, state, access_token, scope, refresh_token):

	try:
		state_user = State.objects.get(nonce=state).user
	except State.DoesNotExist: return False

	if not user == state_user: return False

	a = AccessToken.objects.create(user=user, token=access_token, refresh_token=refresh_token)
	a.scope.add(Scope.objects.get(scope=scope))
	a.save()
	return True
