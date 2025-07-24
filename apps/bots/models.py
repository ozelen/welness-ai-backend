from django.db import models
from django.contrib.auth.models import User
from django.utils.functional import cached_property
from telegrinder import Telegrinder, API, Token
import threading
import logging

# Create your models here.

logger = logging.getLogger(__name__)

class Bot(models.Model):
    PROVIDER_CHOICES = [
        ('telegram', 'Telegram'),
        ('whatsapp', 'WhatsApp'),
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('twitter', 'Twitter'),
    ]
        
    name = models.CharField(max_length=255)
    provider = models.CharField(max_length=255, choices=PROVIDER_CHOICES, default='telegram')
    api_key = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class UserContext(models.Model):
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    external_id = models.CharField(max_length=255)
    context = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username
