from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
  name = models.CharField(max_length=200, null=True)
  email = models.EmailField(unique=True, null=True)
  bio = models.TextField(null=True)
  
  avatar = models.ImageField(null=True, default='avatar.svg')
  
  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS = []

class Topic(models.Model):
  name = models.CharField(max_length=150)
  
  
  def __str__(self):
    return self.name

class Hive(models.Model):
  creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
  topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
  buzz = models.CharField(max_length=150)
  details = models.TextField(null=True, blank=True)
  members = models.ManyToManyField(User, related_name='members', blank=True)
  updated = models.DateTimeField(auto_now=True) #auto timestamp
  created_at = models.DateTimeField(auto_now_add=True)
  theme = models.CharField(max_length=10, choices=[('light', 'Light'), ('dark', 'Dark')], default='dark')
  
  STATUS_CHOICES = (
        ('public', 'Public'),
        ('private', 'Private'),
  )
  status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='public')
  password = models.CharField(max_length=255, blank=True, null=True)  # Used only for private hives
  
  class Meta:
    ordering = ['-updated', '-created_at']
    
  def __str__(self):
    return self.buzz


class Message(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  hive = models.ForeignKey(Hive, on_delete=models.CASCADE) #delete all msgs with the room
  body = models.TextField(blank=True, null=True)
  file = models.FileField(upload_to='files/', blank=True, null=True)
  updated = models.DateTimeField(auto_now=True) #auto timestamp
  created_at = models.DateTimeField(auto_now_add=True)
  is_pinned = models.BooleanField(default=False)
  audio = models.FileField(upload_to="voice_messages/", blank=True, null=True)
  vanish_mode = models.BooleanField(default=False) #flag 
  vanish_time = models.DateTimeField(blank=True,null=True) #determines the time after which it will disappear
  


  
  class Meta:
    ordering = ['-updated', '-created_at']
    
    
  def __str__(self):
    return self.body[:50]
  
  def has_vanished(self):
        """Check if the message has vanished based on vanish_time."""
        if self.vanish_mode and self.vanish_time:
            return timezone.now() > self.vanish_time
        return False
      
  
  
  
class HiveMember(models.Model):
  name=models.CharField(max_length=255)
  uid=models.CharField(max_length=200)
  hive_name=models.CharField(max_length=200)

  def __str__(self):
      return self.name
  
  
class UserRole(models.Model):
    ROLE_CHOICES = [
        ('queen', 'Queen'),
        ('moderator', 'Moderator'),
        ('bee', 'Bee'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hive = models.ForeignKey(Hive, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='bee')  # Restrict role choices
    def __str__(self):
        return f"{self.user.username} - {self.role} in {self.hive.buzz}"
      
      

class Poll(models.Model):
    hive = models.ForeignKey(Hive, on_delete=models.CASCADE, related_name="polls")
    question = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question

class Option(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="options")
    text = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.text} ({self.poll.question})"

class Vote(models.Model):
    option = models.ForeignKey(Option, on_delete=models.CASCADE, related_name="votes")
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('option', 'user')  # Prevent duplicate votes per user per option
        
        
