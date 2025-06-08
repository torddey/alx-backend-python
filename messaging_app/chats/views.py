from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db.models import Q, Prefetch
from .models import User, Conversation, Message
from .serializers import (
    ConversationSerializer, 
    ConversationBasicSerializer,
    ConversationWithMessagesSerializer,
    MessageSerializer, 
    MessageBasicSerializer,
    UserBasicSerializer
)
from .permissions import (
    IsParticipantOfConversation,
    IsMessageSender,
    CanModifyConversation
)

class StandardResultsSetPagination(PageNumberPagination):
    """
    Custom pagination class for conversations and messages.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing conversations.
    Provides CRUD operations and custom actions for conversations.
    """
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipantOfConversation]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """
        Filter conversations to only include those where the current user is a participant.
        """
        user = self.request.user
        return Conversation.objects.filter(
            participants=user
        ).prefetch_related(
            'participants',
            Prefetch(
                'messages',
                queryset=Message.objects.select_related('sender').order_by('-sent_at')
            )
        ).distinct().order_by('-created_at')
    
    def get_serializer_class(self):
        """
        Return different serializers based on the action.
        """
        if self.action == 'list':
            return ConversationBasicSerializer
        elif self.action == 'retrieve':
            return ConversationWithMessagesSerializer
        elif self.action == 'messages':
            return MessageBasicSerializer
        return ConversationSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Create a new conversation and automatically add the creator as a participant.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create conversation
        conversation = serializer.save()
        
        # Add the creator as a participant if not already included
        if not conversation.participants.filter(user_id=request.user.user_id).exists():
            conversation.participants.add(request.user)
        
        # Return the created conversation with full details
        response_serializer = ConversationWithMessagesSerializer(conversation)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a specific conversation with messages.
        """
        conversation = self.get_object()
        serializer = self.get_serializer(conversation)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], url_path='messages')
    def messages(self, request, pk=None):
        """
        Get paginated messages for a specific conversation.
        """
        conversation = self.get_object()
        messages = conversation.messages.select_related('sender').order_by('-sent_at')
        
        # Apply pagination
        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = MessageBasicSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = MessageBasicSerializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='add-participant')
    def add_participant(self, request, pk=None):
        """
        Add a participant to an existing conversation.
        """
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        if not user_id:
            return Response(
                {'error': 'user_id is required.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user_to_add = User.objects.get(user_id=user_id)
            conversation.participants.add(user_to_add)
            return Response(
                {'message': f'User {user_to_add.username} added to conversation.'}, 
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found.'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'], url_path='remove-participant')
    def remove_participant(self, request, pk=None):
        """
        Remove a participant from an existing conversation.
        """
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        if not user_id:
            return Response(
                {'error': 'user_id is required.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user_to_remove = User.objects.get(user_id=user_id)
            conversation.participants.remove(user_to_remove)
            return Response(
                {'message': f'User {user_to_remove.username} removed from conversation.'}, 
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found.'}, 
                status=status.HTTP_404_NOT_FOUND
            )

class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing messages.
    Provides CRUD operations for messages within conversations.
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipantOfConversation, IsMessageSender]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """
        Filter messages to only include those from conversations where the user is a participant.
        """
        user = self.request.user
        return Message.objects.filter(
            conversation__participants=user
        ).select_related('sender', 'conversation').order_by('-sent_at')
    
    def create(self, request, *args, **kwargs):
        """
        Create a new message in a conversation.
        """
        data = request.data.copy()
        data['sender_id'] = str(request.user.user_id)  # Convert UUID to string
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        message = serializer.save()
        response_serializer = MessageSerializer(message)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a specific message.
        """
        message = self.get_object()
        serializer = self.get_serializer(message)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        """
        Update a message (only by the sender).
        """
        message = self.get_object()
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete a message (only by the sender).
        """
        message = self.get_object()
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'], url_path='conversation/(?P<conversation_id>[^/.]+)')
    def by_conversation(self, request, conversation_id=None):
        """
        Get all messages for a specific conversation.
        """
        try:
            conversation = Conversation.objects.get(conversation_id=conversation_id)
            messages = conversation.messages.select_related('sender').order_by('sent_at')
            
            # Apply pagination
            page = self.paginate_queryset(messages)
            if page is not None:
                serializer = MessageBasicSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = MessageBasicSerializer(messages, many=True)
            return Response(serializer.data)
            
        except Conversation.DoesNotExist:
            return Response(
                {'error': 'Conversation not found.'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        """
        Search messages by content.
        """
        query = request.query_params.get('q', '')
        if not query:
            return Response(
                {'error': 'Search query is required.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        messages = self.get_queryset().filter(
            Q(message_body__icontains=query) | Q(content__icontains=query)
        )
        
        # Apply pagination
        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = MessageBasicSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = MessageBasicSerializer(messages, many=True)
        return Response(serializer.data)