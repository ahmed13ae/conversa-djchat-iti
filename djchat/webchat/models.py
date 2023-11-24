from django.contrib.auth import get_user_model
from django.db import models

def meesage_file_upload_path(instance,filename):
    return f"messages/{instance.id}/{filename}"

class Conversation(models.Model):
    channel_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

class Attachment(models.Model):
    file = models.FileField(upload_to=meesage_file_upload_path)
    sender = models.ForeignKey(get_user_model(),on_delete=models.CASCADE,null=True,default=None,related_name='attatchment')


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="message")
    sender = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    content = models.TextField()
    attachments = models.ManyToManyField(Attachment,blank=True,related_name='messages')
    timestamp = models.DateTimeField(auto_now_add=True)
    
