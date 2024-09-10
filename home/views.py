from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Hive, Topic
from .forms import HiveForm

'''
hive = room
buzz = name
'''
# hives = [
#   {'id': 1, 'buzz': 'Learn Scraping'},
#   {'id': 2, 'buzz': 'Learn Automata'},
#   {'id': 3, 'buzz': 'Learn C++'},
# ]




# Create your views here.
def home(request):
  #get all hives by search
  q = request.GET.get('q') if request.GET.get('q') != None else ''
  hives = Hive.objects.filter(topic__name__icontains = q)
  
  topics = Topic.objects.all()
  
  return render(request, 'home/home.html', {'hives': hives, 'topics': topics})

def hive(request, pk):
  hive = Hive.objects.get(id=pk)
  context = {
    'hive': hive
  }
  return render(request, 'home/hive.html', context)

# CRUD Operations
def createHive(request):
  form = HiveForm()
  if request.method == 'POST':
    form = HiveForm(request.POST) # send all values to form
    if form.is_valid(): # check for valid vals
      form.save()
      return redirect('homepage')
  
  context = {"form": form}
  return render(request, 'home/hiveForm.html', context)


def updateHive(request, pk):
  hive = Hive.objects.get(id=pk)
  form = HiveForm(instance=hive) #pre-fill with values
  
  if request.method == 'POST':  #ensure the current editable hive is updated
    form = HiveForm(request.POST, instance=hive)
    if form.is_valid():
      form.save()
      return redirect('homepage')
    
  return render(request, 'home/hiveForm.html', {'form': form})

def deleteHive(request, pk):
  hive = Hive.objects.get(id=pk)
  if request.method == "POST":
    hive.delete()
    return redirect('homepage')
  
  return render(request, 'home/delete.html', {'obj': hive})