from django.db import models

# Create your models here.
class Survey(models.Model):
	survey_id = models.IntegerField()
	user_id = models.CharField(max_length=48)
	question = models.TextField()
	timestamp = models.DateField(auto_now_add=True)	
