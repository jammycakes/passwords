from django.shortcuts import render
from django.template import RequestContext

# Create your views here.

def index(request):
    rc = RequestContext(request, {})
    return render(request, 'registration/index.html', rc)