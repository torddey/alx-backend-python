from django.urls import path
from .views import message_list, delete_user, delete_user_confirm, delete_user_ajax

urlpatterns = [
    path('messages/', message_list, name='message_list'),
    path('delete-account/', delete_user, name='delete_user'),
    path('delete-account/confirm/', delete_user_confirm, name='delete_user_confirm'),
    path('delete-account/ajax/', delete_user_ajax, name='delete_user_ajax'),
] 