from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q
from .models import Hive, Topic
from .forms import HiveForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

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
def loginView(request):
  username, password = '', ''
  
  page = 'login'
  if request.user.is_authenticated:
    return redirect('homepage')
   
  if request.method == 'POST':
    username = request.POST.get('username')
    password = request.POST.get('password')
    
    user = authenticate(request, username=username, password=password)
    if user is not None:
      login(request, user)
      return redirect('homepage')

    else:
      messages.error(request, "We could not find your username")

  context={'username': username, 'password': password, 'page': login}
  return render(request, 'home/logreg.html', context)
  
def logoutView(request):
  
  logout(request)
  return redirect('homepage')

def registerUser(request):
  context={'page': 'register'}
  return render(request, 'home/logreg.html', context )
  

def home(request):
  ''' 
  search based on topic, buzz, details
  made for ease of users if they dont rmr exact topics etc.
  '''
  
  q = request.GET.get('q') if request.GET.get('q') != None else ''

  hives = Hive.objects.filter(  
    Q(topic__name__icontains = q) |
    Q(buzz__icontains = q) |
    Q(details__icontains = q) 
  )
  
  topics = Topic.objects.all()
  hive_count = hives.count()
  
  context = {'hives': hives, 'topics': topics, 'hive_count': hive_count}
  return render(request, 'home/home.html', context)

def hive(request, pk):
  hive = Hive.objects.get(id=pk)
  context = {
    'hive': hive
  }
  return render(request, 'home/hive.html', context)

# CRUD Operations

@login_required(login_url='login')
def createHive(request):
  form = HiveForm()
  if request.method == 'POST':
    form = HiveForm(request.POST) # send all values to form
    if form.is_valid(): # check for valid vals
      form.save()
      return redirect('homepage')
  
  context = {"form": form}
  return render(request, 'home/hiveForm.html', context)

@login_required(login_url='login')
def updateHive(request, pk):
  hive = Hive.objects.get(id=pk)
  form = HiveForm(instance=hive) #pre-fill with values
  
  if request.user != hive.creator:
    return HttpResponse("Nah fam i can't allow it")
  
  if request.method == 'POST':  #ensure the current editable hive is updated
    form = HiveForm(request.POST, instance=hive)
    if form.is_valid():
      form.save()
      return redirect('homepage')
    
  return render(request, 'home/hiveForm.html', {'form': form})

@login_required(login_url='login')
def deleteHive(request, pk):
  hive = Hive.objects.get(id=pk)
  
  if request.user != hive.creator:
    return HttpResponse("Nah fam i can't allow it")
  
  if request.method == "POST":
    hive.delete()
    return redirect('homepage')
  
  return render(request, 'home/delete.html', {'obj': hive})