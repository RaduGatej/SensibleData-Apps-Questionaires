from .models import *

def getUserAuthorization(user):
	try:
		auth = AccessToken.objects.get(user=user)
	except AccessToken.DoesNotExist:
		auth = None
	return auth
