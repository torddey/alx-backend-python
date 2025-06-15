from django.urls import path
from .views import (
    message_list, delete_user, delete_user_confirm, delete_user_ajax,
    thread_list, thread_detail, conversation_threads, send_message, reply_to_message
)

urlpatterns = [
    path('messages/', message_list, name='message_list'),
    path('threads/', thread_list, name='thread_list'),
    path('threads/<uuid:thread_id>/', thread_detail, name='thread_detail'),
    path('conversation/<uuid:other_user_id>/', conversation_threads, name='conversation_threads'),
    path('send-message/', send_message, name='send_message'),
    path('reply/', reply_to_message, name='reply_to_message'),
    path('delete-account/', delete_user, name='delete_user'),
    path('delete-account/confirm/', delete_user_confirm, name='delete_user_confirm'),
    path('delete-account/ajax/', delete_user_ajax, name='delete_user_ajax'),
] 