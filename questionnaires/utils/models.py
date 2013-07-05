from django.db import models
from django.contrib.auth.models import User

class Scope(models.Model):
        scope = models.CharField(unique=True, max_length=100, db_index=True)
        description = models.TextField(blank=True)
        def __unicode__(self):
                return self.scope

class AccessToken(models.Model):
	user = models.ForeignKey(User)
	token = models.CharField(unique=True, max_length=100, db_index=True)
    	refresh_token = models.CharField(unique=True, blank=True, null=True, max_length=100, db_index=True)
	scope = models.ManyToManyField(Scope)
