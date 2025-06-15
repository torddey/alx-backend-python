from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.db.models import Q
from .models import Message, Notification, MessageHistory
from django.db import models
from chats.models import User

def message_list(request):
    messages = Message.objects.select_related('sender', 'receiver', 'edited_by').prefetch_related('history').all()
    return render(request, 'messaging/message_list.html', {'messages': messages})

@login_required
def thread_list(request):
    """Display all threads for the current user"""
    user = request.user
    threads = Message.get_user_threads(user)
    
    # Get conversation partners for each thread
    for thread in threads:
        if thread.sender == user:
            thread.conversation_partner = thread.receiver
        else:
            thread.conversation_partner = thread.sender
    
    return render(request, 'messaging/thread_list.html', {
        'threads': threads,
        'user': user
    })

@login_required
def thread_detail(request, thread_id):
    """Display a specific thread with all its replies"""
    user = request.user
    thread = get_object_or_404(Message, message_id=thread_id)
    
    # Check if user is part of this conversation
    if thread.sender != user and thread.receiver != user:
        messages.error(request, "You don't have permission to view this thread.")
        return redirect('thread_list')
    
    # Get all messages in the thread (root + replies)
    thread_messages = thread.get_thread_messages()
    
    # Get conversation partner
    if thread.sender == user:
        conversation_partner = thread.receiver
    else:
        conversation_partner = thread.sender
    
    return render(request, 'messaging/thread_detail.html', {
        'thread': thread,
        'thread_messages': thread_messages,
        'conversation_partner': conversation_partner,
        'user': user
    })

@login_required
def conversation_threads(request, other_user_id):
    """Display all threads between current user and another user"""
    user = request.user
    other_user = get_object_or_404(User, user_id=other_user_id)
    
    threads = Message.get_threaded_conversations(user, other_user)
    
    return render(request, 'messaging/conversation_threads.html', {
        'threads': threads,
        'other_user': other_user,
        'user': user
    })

@login_required
@require_POST
@csrf_protect
def send_message(request):
    """Send a new message or reply"""
    user = request.user
    receiver_id = request.POST.get('receiver_id')
    content = request.POST.get('content')
    parent_message_id = request.POST.get('parent_message_id')
    
    if not content or not receiver_id:
        return JsonResponse({
            'success': False,
            'message': 'Missing required fields'
        }, status=400)
    
    try:
        receiver = User.objects.get(user_id=receiver_id)
        
        # Create the message with sender=request.user
        message_data = {
            'sender': user,  # This ensures sender=request.user
            'receiver': receiver,
            'content': content
        }
        
        # If this is a reply, add parent message
        if parent_message_id:
            parent_message = get_object_or_404(Message, message_id=parent_message_id)
            message_data['parent_message'] = parent_message
        
        message = Message.objects.create(**message_data)
        
        return JsonResponse({
            'success': True,
            'message': 'Message sent successfully',
            'message_id': str(message.message_id),
            'timestamp': message.timestamp.isoformat()
        })
        
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Receiver not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error sending message: {str(e)}'
        }, status=500)

@login_required
@require_POST
@csrf_protect
def reply_to_message(request):
    """Reply to a specific message"""
    user = request.user
    parent_message_id = request.POST.get('parent_message_id')
    content = request.POST.get('content')
    
    if not content or not parent_message_id:
        return JsonResponse({
            'success': False,
            'message': 'Missing required fields'
        }, status=400)
    
    try:
        parent_message = get_object_or_404(Message, message_id=parent_message_id)
        
        # Determine receiver (the other person in the conversation)
        if parent_message.sender == user:
            receiver = parent_message.receiver
        else:
            receiver = parent_message.sender
        
        # Create reply with sender=request.user
        reply = Message.objects.create(
            sender=user,  # This ensures sender=request.user
            receiver=receiver,
            content=content,
            parent_message=parent_message
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Reply sent successfully',
            'reply_id': str(reply.message_id),
            'timestamp': reply.timestamp.isoformat(),
            'sender_username': user.username
        })
        
    except Message.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Parent message not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error sending reply: {str(e)}'
        }, status=500)

@login_required
def get_user_id(request, username):
    """Get user ID by username for new thread creation"""
    try:
        user = User.objects.get(username=username)
        return JsonResponse({
            'success': True,
            'user_id': str(user.user_id),
            'username': user.username
        })
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': f'User "{username}" not found'
        }, status=404)

@login_required
@require_POST
@csrf_protect
def create_new_thread(request):
    """Create a new thread (message without parent)"""
    user = request.user
    receiver_id = request.POST.get('receiver_id')
    content = request.POST.get('content')
    
    if not content or not receiver_id:
        return JsonResponse({
            'success': False,
            'message': 'Missing required fields'
        }, status=400)
    
    try:
        receiver = User.objects.get(user_id=receiver_id)
        
        # Create new thread with sender=request.user
        new_thread = Message.objects.create(
            sender=user,  # This ensures sender=request.user
            receiver=receiver,
            content=content,
            parent_message=None  # This makes it a new thread
        )
        
        return JsonResponse({
            'success': True,
            'message': 'New thread created successfully',
            'thread_id': str(new_thread.message_id),
            'timestamp': new_thread.timestamp.isoformat()
        })
        
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Receiver not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error creating thread: {str(e)}'
        }, status=500)

@login_required
def delete_user(request):
    """
    View to handle user account deletion
    """
    if request.method == 'POST':
        # Get confirmation from the form
        confirm_delete = request.POST.get('confirm_delete')
        
        if confirm_delete == 'yes':
            user = request.user
            username = user.username
            
            # Log the deletion attempt
            print(f"User {username} is deleting their account via form submission")
            
            # Count related data before deletion
            message_count = Message.objects.filter(
                models.Q(sender=user) | models.Q(receiver=user)
            ).count()
            notification_count = Notification.objects.filter(user=user).count()
            history_count = MessageHistory.objects.filter(edited_by=user).count()
            
            print(f"User {username} has {message_count} messages, {notification_count} notifications, {history_count} history entries")
            
            # Delete the user (this will trigger the pre_delete signal)
            user.delete()
            
            # Add success message (though user won't see it since they're logged out)
            messages.success(request, f'Account for {username} has been successfully deleted.')
            
            # Redirect to home page or login page
            return redirect('login')
        else:
            messages.error(request, 'Account deletion cancelled. Please confirm to delete your account.')
            return redirect('delete_user_confirm')
    
    # GET request - show confirmation page
    return render(request, 'messaging/delete_user_confirm.html')

@login_required
def delete_user_confirm(request):
    """
    Confirmation page for account deletion
    """
    user = request.user
    
    # Count user's data for display
    message_count = Message.objects.filter(
        models.Q(sender=user) | models.Q(receiver=user)
    ).count()
    notification_count = Notification.objects.filter(user=user).count()
    history_count = MessageHistory.objects.filter(edited_by=user).count()
    
    context = {
        'message_count': message_count,
        'notification_count': notification_count,
        'history_count': history_count,
    }
    
    return render(request, 'messaging/delete_user_confirm.html', context)

@login_required
@require_POST
@csrf_protect
def delete_user_ajax(request):
    """
    AJAX endpoint for account deletion
    """
    try:
        user = request.user
        username = user.username
        
        # Log the deletion
        print(f"User {username} is deleting their account via AJAX")
        
        # Count related data before deletion
        message_count = Message.objects.filter(
            models.Q(sender=user) | models.Q(receiver=user)
        ).count()
        notification_count = Notification.objects.filter(user=user).count()
        history_count = MessageHistory.objects.filter(edited_by=user).count()
        
        print(f"User {username} has {message_count} messages, {notification_count} notifications, {history_count} history entries")
        
        # Delete the user (this will trigger the pre_delete signal)
        user.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Account for {username} has been successfully deleted.',
            'deleted_data': {
                'messages': message_count,
                'notifications': notification_count,
                'history_entries': history_count
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error deleting account: {str(e)}'
        }, status=500) 