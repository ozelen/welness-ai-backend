from django.urls import path
from . import views

app_name = 'planner'

urlpatterns = [
    path('', views.calendar_view, name='calendar'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('log-meal/', views.log_meal, name='log_meal'),
    path('log-activity/', views.log_activity, name='log_activity'),
]
