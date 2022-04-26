from typing import List
from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import CreateView
from .models import Coral

class CoralCreate(CreateView):
  model = Coral
  fields = '__all__'

# Create your views here.
def home(request):
  return HttpResponse('<h1>Hello!</h1>')

def about(request):
  return render(request, 'about.html')

def corals_index(request):
  corals = Coral.objects.all()
  return render(request, 'corals/index.html', {'corals': corals})

def corals_detail(request, coral_id):
  coral = Coral.objects.get(id=coral_id)
  return render(request, 'corals/detail.html', {'coral': coral})