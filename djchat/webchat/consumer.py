from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from django.contrib.auth import get_user_model
from .models import Conversation, Message
from .serializers import MessageSerializer

User = get_user_model()

class WebChatConsumer(JsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channel_id = None
        # username
        self.user = None

    def connect(self):
        # To accept the connection call
        self.accept()
        # get channel_id from request data
        self.channel_id = self.scope["url_route"]["kwargs"]["channelId"]
        self.user = User.objects.get(id=1)

        # async_to_sync(self.channel_layer.group_add)(
        #     self.channel_id,
        #     self.channel_name,
        #     )
        async_to_sync(self._group_add)()

    def receive_json(self, content):
        channel_id = self.channel_id
        sender = self.user
        message = content["message"]
        attachment = content.get("attachment", None)

        conversation, created = Conversation.objects.get_or_create(channel_id=channel_id)
        
        new_message = Message.objects.create(
            conversation=conversation, sender=sender, content=message, attachment=attachment
        )
        # async_to_sync(self.channel_layer.group_send)(
        #     self.channel_id,
        #     {
        #         "type": "chat.message",
        #         "new_message": {
        #             # "id": new_message.id,
        #             # "sender": new_message.sender.username,
        #             # "content": new_message.content,
        #             # "attachment": str(new_message.attachment.url) if new_message.attachment else None,
        #             # "timestamp": new_message.timestamp.isoformat(),
        #         }
        #     }
        # )
        async_to_sync(self._group_send)(
            {
                "type": "chat.message",
                "new_message": MessageSerializer(new_message).data
            }
        )
        

    def chat_message(self,event):
        # Called when a message is received from the group.
        # Sends the message to the client.
        self.send_json(event)


    # def disconnect(self, close_code):
    #     # removing the current WebSocket consumer instance from the corresponding channel group
    #     async_to_sync(self.channel_layer.group_discard)(self.channel_id, self.channel_name)
    #     super().disconnect(close_code)

    def disconnect(self, close_code):
        async_to_sync(self._group_discard)()
        super().disconnect(close_code)

    def _group_add(self):
        async_to_sync(self.channel_layer.group_add)(self.channel_id, self.channel_name)

    def _group_send(self, message):
        async_to_sync(self.channel_layer.group_send)(self.channel_id, message)

    def _group_discard(self):
        async_to_sync(self.channel_layer.group_discard)(self.channel_id, self.channel_name)