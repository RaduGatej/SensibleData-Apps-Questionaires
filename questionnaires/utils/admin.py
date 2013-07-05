from .models import *
from django.contrib import admin

class ScopeAdmin(admin.ModelAdmin):
        list_display = ('scope', 'description')
        class Meta:
                verbose_name = 'scope'

admin.site.register(Scope, ScopeAdmin)

class AccessTokenAdmin(admin.ModelAdmin):
        list_display = ('user', 'token')

admin.site.register(AccessToken, AccessTokenAdmin)

class StateAdmin(admin.ModelAdmin):
        list_display = ('user', 'nonce')

admin.site.register(State, StateAdmin)
