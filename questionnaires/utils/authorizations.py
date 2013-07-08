from .models import *

def getUserAuthorization(user):
	try:
		auth = AccessToken.objects.get(user=user, type='data')
	except AccessToken.DoesNotExist:
		auth = None
	return auth
