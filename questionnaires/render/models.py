from django.db import models
from django.contrib.auth.models import User

class Response(models.Model):
	user = models.ForeignKey(User)
	form_version = models.CharField(max_length=64)
	variable_name = models.CharField(max_length=30)
	response = models.CharField(max_length=30)
	last_answered = models.DateField(auto_now=True)
	synced_with_study = models.BooleanField(default=False)

	@property
	def details( self ):
		return repr( dict( user_id=self.user_id, form_version=self.form_version, variable_name=self.variable_name,\
							response = self.response, last_answered=self.last_answered ) )

#class Progress(models.Model):
#	user_id = models.CharField(max_length=64);
#	form_version = models.CharField(max_length=64);
#	question_variable_name = models.CharField(max_length=30);

#	@property
#	def details(self):
#		return repr( dict( user_id = self.user_id, form_version = self.form_version, question_variable_name = self.question_variable_name))

