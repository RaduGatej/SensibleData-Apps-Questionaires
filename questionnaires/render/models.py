from django.db import models

class Response(models.Model):
	user_id = models.CharField(max_length=64);
	form_version = models.CharField(max_length=64);
	variable_name = models.CharField(max_length=30);
	response = models.CharField(max_length=30);
	last_answered = models.DateField(auto_now=True);
