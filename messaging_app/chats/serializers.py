from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from .models import User, Conversation, Message, MessageHistory


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model with password handling.
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'user_id', 'username', 'email', 'first_name', 
            'last_name', 'phone_number', 'password', 'password_confirm',
            'date_joined', 'last_login', 'is_active'
        ]
        read_only_fields = ['user_id', 'date_joined', 'last_login']

    def validate(self, attrs):
        """
        Validate that password and password_confirm match.
        """
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError("Password fields didn't match.")
        return attrs

    def create(self, validated_data):
        """
        Create a new user with encrypted password.
        """
        validated_data.pop('password_confirm', None)
        user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        """
        Update user instance, handling password separately.
        """
        password = validated_data.pop('password', None)
        validated_data.pop('password_confirm', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance


class UserBasicSerializer(serializers.ModelSerializer):
    """
    Basic user serializer for nested relationships.
    """
    class Meta:
        model = User
        fields = ['user_id', 'username', 'first_name', 'last_name', 'email']


class MessageHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for MessageHistory model.
    """
    edited_by = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = MessageHistory
        fields = [
            'history_id', 'old_content', 'edited_at', 'edited_by'
        ]
        read_only_fields = ['history_id', 'edited_at']


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for Message model with sender details and edit history.
    """
    sender = UserBasicSerializer(read_only=True)
    sender_id = serializers.UUIDField(write_only=True)
    history = MessageHistorySerializer(many=True, read_only=True)
    
    class Meta:
        model = Message
        fields = [
            'message_id', 'conversation', 'sender', 'sender_id',
            'content', 'timestamp', 'edited', 'edited_at', 'history'
        ]
        read_only_fields = ['message_id', 'timestamp', 'edited', 'edited_at']

    def create(self, validated_data):
        """
        Create a new message.
        """
        sender_id = validated_data.pop('sender_id')
        try:
            sender = User.objects.get(user_id=sender_id)
            validated_data['sender'] = sender
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid sender ID.")
        
        return Message.objects.create(**validated_data)


class MessageBasicSerializer(serializers.ModelSerializer):
    """
    Basic message serializer for nested relationships.
    """
    sender = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = [
            'message_id', 'sender', 'content', 'timestamp', 'edited', 'edited_at'
        ]


class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for Conversation model with nested messages and participants.
    """
    participants = UserBasicSerializer(many=True, read_only=True)
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(), 
        write_only=True, 
        required=False
    )
    messages = MessageBasicSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id', 'participants', 'participant_ids', 
            'messages', 'message_count', 'last_message', 'created_at'
        ]
        read_only_fields = ['conversation_id', 'created_at']

    def get_message_count(self, obj):
        """
        Get the total number of messages in the conversation.
        """
        return obj.messages.count()

    def get_last_message(self, obj):
        """
        Get the most recent message in the conversation.
        """
        last_message = obj.messages.order_by('-sent_at').first()
        if last_message:
            return MessageBasicSerializer(last_message).data
        return None

    def create(self, validated_data):
        """
        Create a new conversation with participants.
        """
        participant_ids = validated_data.pop('participant_ids', [])
        conversation = Conversation.objects.create(**validated_data)
        
        if participant_ids:
            try:
                participants = User.objects.filter(user_id__in=participant_ids)
                conversation.participants.set(participants)
            except Exception as e:
                conversation.delete()
                raise serializers.ValidationError(f"Error adding participants: {str(e)}")
        
        return conversation

    def update(self, instance, validated_data):
        """
        Update conversation, handling participants separately.
        """
        participant_ids = validated_data.pop('participant_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if participant_ids is not None:
            try:
                participants = User.objects.filter(user_id__in=participant_ids)
                instance.participants.set(participants)
            except Exception as e:
                raise serializers.ValidationError(f"Error updating participants: {str(e)}")
        
        instance.save()
        return instance


class ConversationBasicSerializer(serializers.ModelSerializer):
    """
    Basic conversation serializer without nested messages (for performance).
    """
    participants = UserBasicSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id', 'participants', 'message_count', 
            'last_message', 'created_at'
        ]

    def get_message_count(self, obj):
        """
        Get the total number of messages in the conversation.
        """
        return obj.messages.count()

    def get_last_message(self, obj):
        """
        Get the most recent message in the conversation.
        """
        last_message = obj.messages.order_by('-sent_at').first()
        if last_message:
            return {
                'message_id': str(last_message.message_id),
                'message_body': last_message.message_body,
                'sent_at': last_message.sent_at,
                'sender': last_message.sender.username
            }
        return None


class ConversationWithMessagesSerializer(serializers.ModelSerializer):
    """
    Detailed conversation serializer with paginated messages.
    """
    participants = UserBasicSerializer(many=True, read_only=True)
    messages = MessageBasicSerializer(many=True, read_only=True)
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id', 'participants', 'messages', 'created_at'
        ]