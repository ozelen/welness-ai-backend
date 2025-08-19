from django.urls import path
from . import views

app_name = 'activities'

urlpatterns = [
    # Calendar and management pages
    path('calendar/', views.activities_calendar_view, name='calendar'),
    path('manage/', views.activities_management_page, name='manage'),
    
                    # Activity CRUD
                path('create/', views.create_activity, name='create_activity'),
                path('get/<int:activity_id>/', views.get_activity_data, name='get_activity_data'),
                path('update/<int:activity_id>/', views.update_activity, name='update_activity'),
                path('delete/<int:activity_id>/', views.delete_activity, name='delete_activity'),
                path('schedule/', views.schedule_activity, name='schedule_activity'),
    path('toggle-completion/<int:activity_id>/', views.toggle_activity_completion, name='toggle_activity_completion'),
    
    # Activity records
    path('log/', views.create_activity_record, name='create_activity_record'),
    path('delete-record/<int:record_id>/', views.delete_activity_record, name='delete_activity_record'),
    
    # Exercises
    path('exercises/create/', views.create_exercise, name='create_exercise'),
    path('exercises/delete/<int:exercise_id>/', views.delete_exercise, name='delete_exercise'),
    path('exercises/suggestions/', views.exercise_suggestions, name='exercise_suggestions'),
    
    # Activity exercises
    path('activity-exercises/create/', views.create_activity_exercise, name='create_activity_exercise'),
    path('activity-exercises/delete/<int:exercise_id>/', views.delete_activity_exercise, name='delete_activity_exercise'),
]
