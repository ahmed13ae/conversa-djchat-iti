from rest_framework import viewsets
from rest_framework.response import Response

from .models import Conversation
from .schemas import list_message_docs,list_conversation_docs
from .serializers import MessageSerializer,ConversationSerializer


class ConversationViewSet(viewsets.ViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    
    @list_conversation_docs
    def list(self,request):
        channel_id = self.request.query_params.get('channel_id', None)
        try:
            if channel_id:
                conversations = Conversation.objects.filter(channel_id=channel_id)
            else:
                conversations = Conversation.objects.all()

            serializer = self.serializer_class(conversations, many=True)
            return Response(serializer.data)
        except Conversation.DoesNotExist:
            return Response([])



class MessageViewSet(viewsets.ViewSet):
    @list_message_docs
    def list(self, request):
        channel_id = request.query_params.get("channel_id")
        content_query = request.query_params.get("content")  
        try:
            conversation = Conversation.objects.get(channel_id=channel_id)
            message = conversation.message.all()
            # Apply content filter if 'content' parameter is provided
            if content_query:
                message = message.filter(content__icontains=content_query)
            serializer = MessageSerializer(message, many=True)
            return Response(serializer.data)
        except Conversation.DoesNotExist:
            return Response([])
