from django.db import models
from django.contrib.auth.models import User 

# Create your models here.

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
  
  class Meta:
    ordering = ['-updated', '-created_at']
    
  def __str__(self):
    return self.buzz


class Message(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  hive = models.ForeignKey(Hive, on_delete=models.CASCADE) #delete all msgs with the room
  body = models.TextField()
  updated = models.DateTimeField(auto_now=True) #auto timestamp
  created_at = models.DateTimeField(auto_now_add=True)
  
  class Meta:
    ordering = ['-updated', '-created_at']
    
    
  def __str__(self):
    return self.body[:50]
  
  
  