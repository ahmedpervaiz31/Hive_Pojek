from django.db import models
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

  
  class Meta:
    ordering = ['-updated', '-created_at']
    
    
  def __str__(self):
    return self.body[:50]
  
  
  
class HiveMember(models.Model):
  name=models.CharField(max_length=255)
  uid=models.CharField(max_length=200)
  hive_name=models.CharField(max_length=200)

  def __str__(self):
      return self.name
  
  