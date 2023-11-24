from rest_framework import serializers

from .models import Message,Conversation,Attachment

class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ('id', 'channel_id', 'created_at')

class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ['id', 'file']

class MessageSerializer(serializers.ModelSerializer):
    # username -> str
    sender = serializers.StringRelatedField()
    attachments = AttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = Message
        fields = ["id", "sender", "content","attachments", "timestamp"]