from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template import RequestContext
from django.contrib.auth.forms import UserCreationForm

# Create your views here.

def index(request):
    rc = RequestContext(request, {})
    return render(request, 'registration/index.html', rc)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/')
    else:
        form = UserCreationForm()

    rc = RequestContext(request, { 'form': form })
    return render(request, 'registration/register.html', rc)

def profile(request):
    return HttpResponseRedirect('/')