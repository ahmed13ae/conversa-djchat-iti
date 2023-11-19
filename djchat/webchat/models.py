from django.contrib.auth import get_user_model
from django.db import models

def meesage_file_upload_path(instance,filename):
    return f"messages/{instance.id}/file/{filename}"

class Conversation(models.Model):
    channel_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="message")
    sender = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    content = models.TextField()
    attachment = models.FileField(blank=True, null=True, upload_to=meesage_file_upload_path)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-timestamp',)
