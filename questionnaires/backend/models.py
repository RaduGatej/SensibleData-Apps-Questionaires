from django.db import models

class Survey(models.Model):
	survey_id = models.IntegerField()
	user_id = models.CharField(max_length=48)
	question = models.TextField()
	timestamp = models.DateField(auto_now_add=True)	
