from django.urls import path, include
import Users.views as views

urlpatterns = [
    path('login', views.login),
    path('register', views.register),
    path('modify_user_status', views.modify_user_status),
    path('get_user_status',views.get_user_status),
    path('get_user_profile',views.get_user_profile),
    path('modify_password', views.modify_password),
    path('modify_user_profile', views.modify_user_profile),
    path('add_star', views.add_star),
    path('delete_star', views.delete_star),
  

]
