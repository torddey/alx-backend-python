from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the object.
        return obj.user == request.user


class IsParticipantOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to access it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Check if user is a participant in the conversation
        if hasattr(obj, 'participants'):
            # For Conversation objects
            return obj.participants.filter(user_id=request.user.user_id).exists()
        elif hasattr(obj, 'conversation'):
            # For Message objects
            return obj.conversation.participants.filter(user_id=request.user.user_id).exists()
        
        return False


class IsMessageSender(permissions.BasePermission):
    """
    Custom permission to only allow message senders to edit/delete their messages.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for participants
        if request.method in permissions.SAFE_METHODS:
            return obj.conversation.participants.filter(user_id=request.user.user_id).exists()
        
        # Write permissions only for the message sender
        return obj.sender.user_id == request.user.user_id


class IsConversationParticipant(permissions.BasePermission):
    """
    Custom permission to only allow conversation participants to access conversation data.
    """
    
    def has_permission(self, request, view):
        # Allow authenticated users to create conversations
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Check if user is a participant in the conversation
        return obj.participants.filter(user_id=request.user.user_id).exists()


class CanModifyConversation(permissions.BasePermission):
    """
    Custom permission to allow conversation participants to modify conversation settings.
    """
    
    def has_object_permission(self, request, view, obj):
        # Only participants can modify conversation
        if not obj.participants.filter(user_id=request.user.user_id).exists():
            return False
        
        # For certain actions, you might want to restrict to conversation creators
        # or admins. For now, all participants can modify.
        return True


class IsUserSelf(permissions.BasePermission):
    """
    Custom permission to only allow users to access their own profile.
    """
    
    def has_object_permission(self, request, view, obj):
        # Check if the user is accessing their own profile
        return obj.user_id == request.user.user_id


class CanAccessUserData(permissions.BasePermission):
    """
    Custom permission for user data access with different levels.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Users can access their own data
        if obj.user_id == request.user.user_id:
            return True
        
        # Allow read-only access to basic user info for conversation participants
        if request.method in permissions.SAFE_METHODS:
            # Check if users share any conversations
            shared_conversations = request.user.conversations.filter(
                participants=obj
            ).exists()
            return shared_conversations
        
        return False


class IsOwnerOrParticipant(permissions.BasePermission):
    """
    Combined permission for objects that can be accessed by owners or participants.
    """
    
    def has_object_permission(self, request, view, obj):
        # Check if user is the owner
        if hasattr(obj, 'user') and obj.user.user_id == request.user.user_id:
            return True
        
        # Check if user is a participant (for conversations)
        if hasattr(obj, 'participants'):
            return obj.participants.filter(user_id=request.user.user_id).exists()
        
        # Check if user is a participant through conversation (for messages)
        if hasattr(obj, 'conversation'):
            return obj.conversation.participants.filter(user_id=request.user.user_id).exists()
        
        return False


class ReadOnlyForNonParticipants(permissions.BasePermission):
    """
    Allow read-only access for non-participants, full access for participants.
    """
    
    def has_object_permission(self, request, view, obj):
        # Check if user is a participant
        is_participant = False
        
        if hasattr(obj, 'participants'):
            is_participant = obj.participants.filter(user_id=request.user.user_id).exists()
        elif hasattr(obj, 'conversation'):
            is_participant = obj.conversation.participants.filter(user_id=request.user.user_id).exists()
        
        # Participants have full access
        if is_participant:
            return True
        
        # Non-participants have read-only access
        return request.method in permissions.SAFE_METHODS


class DenyAll(permissions.BasePermission):
    """
    Permission class that denies all access.
    """
    
    def has_permission(self, request, view):
        return False
    
    def has_object_permission(self, request, view, obj):
        return False


class AllowAny(permissions.BasePermission):
    """
    Permission class that allows any access.
    """
    
    def has_permission(self, request, view):
        return True
    
    def has_object_permission(self, request, view, obj):
        return True