from django.urls import path
from . import views

urlpatterns = [
    path('api/chat/', views.chat_endpoint, name='chat_endpoint'),
    path('api/chat/history/<int:user_id>/', views.chat_history, name='chat_history'),
] 