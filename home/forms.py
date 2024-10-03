from django.forms import ModelForm
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Hive, User

class myUserCreationForm(UserCreationForm):
  class Meta:
    model = User
    fields = ['name', 'username', 'email', 'password1', 'password2' ]

class HiveForm(ModelForm):
  class Meta:
    model = Hive
    fields = '__all__'
    exclude = ['creator', 'members']

class UserForm(ModelForm):
  class Meta:
    model = User 
    fields = ['name', 'username', 'email', 'bio', 'avatar']