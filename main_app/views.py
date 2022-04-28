from typing import List
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from .models import Coral, Location, Photo
from .forms import NoteForm
import uuid
import boto3

S3_BASE_URL = 'https://s3-us-west-1.amazonaws.com/'
BUCKET = 'the-frag-tank'

class CoralCreate(CreateView):
  model = Coral
  fields = ['trade_name', 'scientific_name', 'coral_type', 'difficulty', 'lighting', 'water_flow']

class CoralUpdate(UpdateView):
  model = Coral
  fields = ['scientific_name', 'coral_type', 'difficulty', 'lighting', 'water_flow']

class CoralDelete(DeleteView):
  model = Coral
  success_url = '/corals/'

class LocationList(ListView):
  model = Location

class LocationDetail(DetailView):
  model = Location

class LocationCreate(CreateView):
  model = Location
  fields = '__all__'

class LocationUpdate(UpdateView):
  model = Location
  fields = '__all__'

class LocationDelete(DeleteView):
  model = Location
  success_url = '/locations/'

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
  unused_locations = Location.objects.exclude(id__in = coral.locations.all().values_list('id'))
  note_form = NoteForm()
  return render(request, 'corals/detail.html', {
    'coral': coral, 'note_form': note_form,
    'locations': unused_locations
  })

def add_note(request, coral_id):
  form = NoteForm(request.POST)
  # validate the form
  if form.is_valid():
    new_note = form.save(commit=False)
    new_note.coral_id = coral_id
    new_note.save()
  return redirect('detail', coral_id=coral_id)

def assoc_location(request, coral_id, location_id):
  Coral.objects.get(id=coral_id).locations.add(location_id)
  return redirect('detail', coral_id=coral_id)

def add_photo(request, coral_id):
    # photo-file will be the "name" attribute on the <input type="file">
    photo_file = request.FILES.get('photo-file', None)
    if photo_file:
        s3 = boto3.client('s3')
        # need a unique "key" for S3 / needs image file extension too
        key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
        # just in case something goes wrong
        try:
            s3.upload_fileobj(photo_file, BUCKET, key)
            # build the full url string
            url = f"{S3_BASE_URL}{BUCKET}/{key}"
            # we can assign to cat_id or cat (if you have a cat object)
            Photo.objects.create(url=url, coral_id=coral_id)
        except:
            print('An error occurred uploading file to S3')
    return redirect('detail', coral_id=coral_id)