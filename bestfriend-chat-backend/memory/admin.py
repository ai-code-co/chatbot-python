from django.contrib import admin

# Register your models here.
from .models import UserMemory, ConversationMessage, ConversationSummary



admin.site.register(UserMemory)
admin.site.register(ConversationMessage)
admin.site.register(ConversationSummary)    

# Register your models here.    
