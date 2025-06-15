from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from .models import Message

def message_list(request):
    messages = Message.objects.select_related('sender', 'receiver', 'edited_by').prefetch_related('history').all()
    return render(request, 'messaging/message_list.html', {'messages': messages})

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
            print(f"User {username} is deleting their account")
            
            # Delete the user (this will trigger the post_delete signal)
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
    return render(request, 'messaging/delete_user_confirm.html')

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
        
        # Delete the user
        user.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Account for {username} has been successfully deleted.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error deleting account: {str(e)}'
        }, status=500) 