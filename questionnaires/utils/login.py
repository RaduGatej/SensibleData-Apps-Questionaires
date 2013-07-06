from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect


@login_required
def do_login(request):
        return redirect('home')
