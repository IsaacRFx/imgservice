from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from collection.forms import SignUpForm
#import Listview
from django.views.generic import ListView
from django.contrib.auth import authenticate, login
from django.db.models import Count
from django.shortcuts import redirect


def register(request):
    if request.method == 'POST':
        f = SignUpForm(request.POST)
        if f.is_valid():
            f.save() #
            username = f.cleaned_data.get('username')
            raw_password = f.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)

            return HttpResponseRedirect('/')

    else:
        f = SignUpForm()

    return render(request, 'registration/registration_form.html', {'form': f})


def index(request):

    if not request.user.is_authenticated:
        return HttpResponseRedirect('/accounts/login/')

    return render(request, 'collection/index.html')
