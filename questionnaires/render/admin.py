from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Response

class ResponseAdmin(admin.ModelAdmin):
	list_display = ('user', 'variable_name', 'response', 'last_answered')

admin.site.register(Response, ResponseAdmin)
