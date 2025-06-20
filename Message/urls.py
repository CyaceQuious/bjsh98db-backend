from django.urls import path, include
import Message.views as views

urlpatterns = [
    path('apply_auth', views.apply_auth, name='apply_auth'),
    path('get_auth_sent', views.get_auth_sent, name='get_auth_sent'),
    path('authenticate',views.authenticate,name='authenticate'),
    path('get_auth_received',views.get_auth_received,name='get_auth_received'),
]