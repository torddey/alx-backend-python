from django.urls import path
from .views import message_list

urlpatterns = [
    path('messages/', message_list, name='message_list'),
] 