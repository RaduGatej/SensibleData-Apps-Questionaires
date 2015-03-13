from django.db import models
from django.contrib.auth.models import User

class Response(models.Model):
	user = models.ForeignKey(User)
	type_id = models.CharField(max_length=64)
	form_version = models.CharField(max_length=64)
	variable_name = models.CharField(max_length=1024)
	response = models.CharField(max_length=1024)
	last_answered = models.DateTimeField(auto_now_add=True)
	#last_answered = models.DateTimeField(auto_now=True)
	synced_with_study = models.BooleanField(default=False)
	human_readable_question = models.CharField(max_length=4096)
	human_readable_response = models.CharField(max_length=1024)

	@property
	def details( self ):
		return repr( dict( user_id=self.user, type_id = self.type_id, form_version=self.form_version, variable_name=self.variable_name,\
							response = self.response, last_answered=self.last_answered ) )
		
class Survey(models.Model):
	form_version = models.CharField(max_length=32)
	created = models.DateTimeField(auto_now_add=True)
	title = models.CharField(max_length=1024)
	content = models.TextField(max_length=pow(2,20)) # 1 MB
	prerequisite = models.CharField(max_length=1024)


#class Progress(models.Model):
#	user_id = models.CharField(max_length=64);
#	form_version = models.CharField(max_length=64);
#	question_variable_name = models.CharField(max_length=30);

#	@property
#	def details(self):
#		return repr( dict( user_id = self.user_id, form_version = self.form_version, question_variable_name = self.question_variable_name))

