from django.urls import path
from . import views

app_name = 'activities'

urlpatterns = [
    path('calendar/', views.activities_calendar_view, name='calendar'),
    path('manage/', views.activities_management_page, name='manage'),
    path('api/toggle-completion/<int:activity_id>/', views.toggle_activity_completion, name='toggle_completion'),
    path('api/create-activity/', views.create_activity, name='create_activity'),
    path('api/create-activity-record/', views.create_activity_record, name='create_activity_record'),
    path('api/delete-activity/<int:activity_id>/', views.delete_activity, name='delete_activity'),
    path('api/delete-activity-record/<int:record_id>/', views.delete_activity_record, name='delete_activity_record'),
]
