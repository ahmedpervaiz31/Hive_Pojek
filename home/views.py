from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.http import JsonResponse
from django.db.models import Q
from .models import Hive, Topic, Message, User
import json
# from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
# from django.contrib.auth.forms import UserCreationForm
from .forms import UserForm, HiveForm, myUserCreationForm
import urllib.parse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.views.decorators.csrf import csrf_exempt




# Create your views here.
def loginView(request):
  username, password = '', ''
  
  page = 'login'
  if request.user.is_authenticated:
    return redirect('homepage')
   
  if request.method == 'POST':
    username = request.POST.get('username').lower()
    password = request.POST.get('password')
    
    user = authenticate(request, username=username, password=password)
    if user is not None:
      login(request, user)
      return redirect('homepage')

    else:
      messages.error(request, "We could not find your username")

  context={'username': username, 'password': password, 'page': login}
  return render(request, 'home/login.html', context)
  
def logoutView(request):
  logout(request)
  return redirect('homepage')


def registerUser(request):
    form = myUserCreationForm()

    if request.method == 'POST':
        form = myUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)  # Log the user in automatically after registration
            return redirect('homepage')  # Redirect to the homepage
        else:
            messages.error(request, 'An error occurred during registration')

    return render(request, 'home/register.html', {'form': form})


def home(request):
  
  ''' 
  search based on topic, buzz, details
  made for ease of users if they dont rmr exact topics etc.
  '''
  q = request.GET.get('q') if request.GET.get('q') else ''
  
  q = urllib.parse.unquote(q)
  
  hives = Hive.objects.filter(
    Q(topic__name__icontains = q) |
    Q(buzz__icontains = q) |
    Q(details__icontains = q)
  )
  
  topics = Topic.objects.all()
  chats = Message.objects.filter(
    Q(hive__topic__name__icontains = q)
  )

  hive_count = hives.count()
  topic_count = topics.count()
  
  context = {'hives': hives, 'topics': topics, 'topic_count': topic_count, 'hive_count': hive_count, "q": q, "chats": chats}
  return render(request, 'home/home.html', context)

# CRUD Operations
def hive(request, pk):
  hive = get_object_or_404(Hive, id=pk)

  chats = hive.message_set.all().order_by('-created_at')  # get all messages for that hive
  title = f"{hive.buzz} - Hive"
  members = hive.members.all()
  
  
  if request.method == 'POST':  # add a new message, along with user
    
    body = request.POST.get('body')
    file = request.FILES.get('file')

    # Validate file type and size
    if file:
        valid_extensions = ['.jpg', '.png', '.pdf', '.docx']
        if not any(file.name.endswith(ext) for ext in valid_extensions):
            messages.error(request, 'Invalid file type')
            return redirect('hive', pk=hive.id)

        if file.size > 5 * 1024 * 1024:  # 5 MB limit
            messages.error(request, 'File too large (max 5MB)')
            return redirect('hive', pk=hive.id)
          
          
    Message.objects.create(  
      user = request.user,
      hive = hive,
      body = body,
      file=file,
      
    )
    hive.members.add(request.user)
    return redirect('hive', pk = hive.id)
    
  context = {
    'hive': hive,
    'chats': chats,
    'title': title,
    'members': members,
  }
  return render(request, 'home/hive.html', context)


def send_message(request, hive_id):
    hive = Hive.objects.get(id=hive_id)

    if request.method == 'POST':
        message_body = request.POST.get('message')

        # Create a new message in the database
        message = Message.objects.create(
            body=message_body,
            hive=hive,
            user=request.user
        )
        
        # Automatically add user to hive
        if request.user not in hive.members.all():
            hive.members.add(request.user)


        # Broadcast the message to the WebSocket group (real-time notification)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"hive_{hive_id}",
            {
                'type': 'hive_message',
                'message': f'{request.user.username} sent a message: {message_body}'
            }
        )

        return redirect('hive', hive_id=hive_id)
      
        
@login_required(login_url='login')
def createHive(request):
    topics = Topic.objects.all()
    form = HiveForm()

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        
        # Get or create the topic from the input
        topic, created = Topic.objects.get_or_create(name=topic_name)

        # Create a new Hive object
        Hive.objects.create(
            creator=request.user,  # Set the creator to the current logged-in user
            topic=topic,           # Use the topic object created or fetched above
            buzz=request.POST.get('buzz'),
            details=request.POST.get('deets')  # Changed 'deets' to match form field names
        )
        
        return redirect('homepage')

    context = {"form": form, "topics": topics}
    return render(request, 'home/hiveForm.html', context)


@login_required(login_url='login')
def updateHive(request, pk):
  hive = Hive.objects.get(id=pk)
  form = HiveForm(instance=hive) #pre-fill with values
  topics = Topic.objects.all()
  if request.user != hive.creator:
    return HttpResponse("Nah fam i can't allow it")
  
  if request.method == 'POST':  #ensure the current editable hive is updated
    form = HiveForm(request.POST, instance=hive)
    if form.is_valid():
      form.save()
      return redirect('homepage')
    
  return render(request, 'home/hiveForm.html', {'form': form, 'topics': topics,})

@login_required(login_url='login')
def deleteHive(request, pk):
  hive = Hive.objects.get(id=pk)
  
  if request.user != hive.creator:
    return HttpResponse("Nah fam i can't allow it")
  
  if request.method == "POST":
    hive.delete()
    return redirect('homepage')
  
  return render(request, 'home/delete.html', {'obj': hive})

@login_required(login_url='login')
def deleteMessage(request, pk):
  message = Message.objects.get(id=pk)
  
  if request.user != message.user:
    return HttpResponse("Nah fam i can't allow it")
  
  if request.method == "POST":
    message.delete()
    return redirect('homepage')
  
  return render(request, 'home/delete.html', {'obj': message})

# def updateMessage(request, pk):
#     message = Message.objects.get(id=pk)
#     form = HiveForm(instance=hive) #pre-fill with values
    
#     if request.user != message.user:
#       return HttpResponse("Nah fam i can't allow it")
    
#     if request.method == 'POST':  #ensure the current editable hive is updated
#       form = HiveForm(request.POST, instance=hive)
#       if form.is_valid():
#         form.save()
#         return redirect('homepage')
      
#     return render(request, 'home/hiveForm.html', {'form': form})


def userProfile(request, pk):
  user = User.objects.get(id=pk)
  hives = user.hive_set.all()
  topics = Topic.objects.filter(hive__in=hives).distinct()
  chats = user.message_set.all()
  context = {
    "user": user,
    "hives": hives,
    "topics": topics,
    "chats": chats,
  }
  return render(request, 'home/profile.html', context)


@login_required(login_url='login')
def updateUser(request):
  user = request.user
  form = UserForm(instance=user)
  
  if request.method == 'POST':
    form = UserForm(request.POST, request.FILES, instance=user)
    if form.is_valid():
      form.save()
      return redirect('user-profile', pk=user.id)
    
  context = {"form": form}
  return render(request, 'home/edit-user.html', context)

@csrf_exempt
def update_hive_theme(request, hive_id):
    if request.method == "POST":
        data = json.loads(request.body)
        theme = data.get("theme", "light")
        hive = Hive.objects.get(id=hive_id)
        hive.theme = theme
        hive.save()
        return JsonResponse({"success": True, "theme": theme})
    return JsonResponse({"success": False}, status=400)