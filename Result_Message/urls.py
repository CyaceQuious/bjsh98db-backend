import Result_Message.views as views
from django.urls import path
urlpatterns = [
    path('feedback', views.feedback, name = 'feedback'),
    path('get_feedback_sent',views.get_feedback_sent, name = 'get_feedback_sent'),
    path('get_feedback_received',views.get_feedback_received,name = 'get_feedback_received'),
    path('reply_feedback',views.reply_feedback,name = 'reply_feedback'),
]