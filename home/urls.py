from django.urls import path
from . import views

urlpatterns = [
  path('login/', views.loginView, name='login'),
  path('register/', views.registerUser, name='register'),
  path('logout/', views.logoutView, name='logout'),
  path('hive/<str:pk>/check_password/',views.check_hive_password,name='check_hive_password'),

  #hive crud ops
  path('', views.home, name="homepage"),
  path('hive/<str:pk>/', views.hive, name="hive"),
  path('create-hive/', views.createHive, name='create-hive'),
  path('update-hive/<str:pk>', views.updateHive, name='update-hive'),
  path('delete-hive/<str:pk>', views.deleteHive, name='delete-hive'),
  path('kick-user/<int:hive_id>/<int:user_id>/', views.kick_user, name='kick-user'),

  #messaging urls
  path('hive/<int:hive_id>/pin-message/<int:message_id>/', views.pin_message, name='pin-message'),
  path('delete-message/<int:message_id>/', views.delete_message, name='delete-message'),
  
  #user profile urls
  path('user/<str:pk>', views.userProfile, name='user-profile'),  
  path('update-user/', views.updateUser, name='edit-user'),
  path("update-hive-theme/<int:hive_id>/", views.update_hive_theme, name="update-hive-theme"),
    
  #videocall urls
  path('lobby/<int:hive_id>',views.lobby,name='lobby'),
  path('hive_video/<int:hive_id>',views.videohive,name='hive-video'),
  path('get_token/',views.getToken,),
  path('create_member/',views.createMember),
  path('get_member/',views.getMember),
  path('delete_member/',views.deleteMember),
  
  #poll urls
  path('hive/<int:hive_id>/polls/', views.poll_list, name='poll_list'),
  path('poll/<int:poll_id>/', views.poll_detail, name='poll_detail'),
  path('vote/<int:option_id>/', views.submit_vote, name='submit_vote'),
  path('hive/<int:hive_id>/create-poll/', views.create_poll, name='create_poll'),
  path('poll/<int:poll_id>/', views.poll_detail, name='poll_detail'),
  path('poll/vote/', views.submit_vote, name='submit_vote'),
]