from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import json

class UserMemory(models.Model):
    """
    Stores important facts and user-level metadata.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    external_id = models.CharField(max_length=128, null=True, blank=True, unique=True)
    facts = models.JSONField(default=dict)  # key->value for persistent facts
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"UserMemory({self.external_id or self.user_id})"


class ConversationMessage(models.Model):
    """
    Raw chat messages — keep recent messages for context and auditing.
    """
    user_memory = models.ForeignKey(UserMemory, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=32)  # "user" or "assistant" or "system"
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)  # e.g. sentiment, topics

    class Meta:
        ordering = ["created_at"]


class ConversationSummary(models.Model):
    """
    Compressed summary of user's long-term conversation history used as "memory"
    """
    user_memory = models.OneToOneField(UserMemory, on_delete=models.CASCADE, related_name="summary")
    summary_text = models.TextField(blank=True, default="")
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Summary for {self.user_memory_id}"