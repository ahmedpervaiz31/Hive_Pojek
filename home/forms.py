from django.forms import ModelForm
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Hive, User, Poll, Option

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
    
    
class PollForm(forms.ModelForm):
    options = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Enter each option on a new line"}),
        help_text="Add poll options, one per line.",
    )

    class Meta:
        model = Poll
        fields = ["question", "options"]

    def save(self, commit=True, hive=None):
        poll = super().save(commit=False)
        if hive:
            poll.hive = hive
        if commit:
            poll.save()
            # Create options
            options_text = self.cleaned_data["options"]
            for option_text in options_text.splitlines():
                if option_text.strip():
                    Option.objects.create(poll=poll, text=option_text.strip())
        return poll