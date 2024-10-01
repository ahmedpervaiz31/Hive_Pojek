from django.forms import ModelForm
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Hive
from django.contrib.auth.models import User 


class HiveForm(ModelForm):
  class Meta:
    model = Hive
    fields = '__all__'
    exclude = ['creator', 'members']

# custom register form
# class RegisterForm(UserCreationForm):
#   username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
#   password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
#   password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}))

#   class Meta:
#     model = User
#     fields = ['username', 'password1', 'password2']
    

class UserForm(ModelForm):
  class Meta:
    model = User 
    fields = ['username', 'email']