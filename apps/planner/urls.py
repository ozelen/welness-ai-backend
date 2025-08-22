from django.urls import path
from . import views, api

app_name = 'planner'

urlpatterns = [
    # Calendar view
    path('', views.calendar_view, name='calendar'),
    path('calendar/', views.calendar_view, name='calendar'),
    
    # Logging endpoints
    path('log-meal/', views.log_meal, name='log_meal'),
    path('log-activity/', views.log_activity, name='log_activity'),
    
    # API endpoints for React scheduler
    path('api/events/', api.get_scheduler_events, name='api_events'),
    path('api/events/create/', api.create_scheduler_event, name='api_create_event'),
    path('api/events/<str:event_id>/', api.update_scheduler_event, name='api_update_event'),
    path('api/events/<str:event_id>/delete/', api.delete_scheduler_event, name='api_delete_event'),
    path('api/test-db/', api.test_database, name='api_test_db'),
    path('api/test-simple/', api.test_simple, name='api_test_simple'),
]
