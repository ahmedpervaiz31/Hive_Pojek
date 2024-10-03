from rest_framework.serializers import ModelSerializer
from home.models import Hive

class HiveSerializer(ModelSerializer):
  class Meta:
    model = Hive
    fields = '__all__'