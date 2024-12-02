from django.urls import path
from . import views

urlpatterns = [
  path('login/', views.loginView, name='login'),
  path('register/', views.registerUser, name='register'),
  path('logout/', views.logoutView, name='logout'),
  # path('index', views.index, name="index"),
  # path("<str:room_name>/", views.room, name="hiveroom"),
  path('', views.home, name="homepage"),
  path('hive/<str:pk>/', views.hive, name="hive"),
  path('create-hive/', views.createHive, name='create-hive'),
  path('update-hive/<str:pk>', views.updateHive, name='update-hive'),
  path('delete-hive/<str:pk>', views.deleteHive, name='delete-hive'),
  #path('delete-message/<str:pk>', views.deleteMessage, name='delete-message'),  
  path('delete-message/<int:message_id>/', views.delete_message, name='delete-message'),
  path('kick-user/<int:hive_id>/<int:user_id>/', views.kick_user, name='kick-user'),
  path('user/<str:pk>', views.userProfile, name='user-profile'),  
  path('update-user/', views.updateUser, name='edit-user'),
  path("update-hive-theme/<int:hive_id>/", views.update_hive_theme, name="update-hive-theme"),
  
  path('lobby/',views.lobby,name='lobby'),
  path('hive_video/',views.videohive,name='hive-video'),
  path('get_token/',views.getToken,),
  path('create_member/',views.createMember),
  path('get_member/',views.getMember),
  path('delete_member/',views.deleteMember),
  path('hive/<int:hive_id>/snake.html', views.snakeGame, name='snake_game'),
  path('hive/<str:pk>/photo-editor/', views.photoEditor, name='photo-editor'),


]