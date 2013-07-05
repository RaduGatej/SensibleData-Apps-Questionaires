from django.http import HttpResponse
import json
from django.contrib.auth.decorators import login_required
import answer_validation

@login_required
def submit(request):
	user = request.user
	#TODO 
	#validate answer
	#store answer
	#return confirmation or failure
	return HttpResponse(json.dumps({'ok':'123'}))
