from django.urls import path
from . import views

urlpatterns = [
  path('', views.home, name="homepage"),
  path('hive/<str:pk>/', views.hive, name="hive"),
  path('create-hive/', views.createHive, name='create-hive'),
  path('update-hive/<str:pk>', views.updateHive, name='update-hive'),
  path('delete-hive/<str:pk>', views.deleteHive, name='delete-hive'),
]