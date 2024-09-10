from django.forms import ModelForm
from .models import Hive


class HiveForm(ModelForm):
  class Meta:
    model = Hive
    fields = '__all__'