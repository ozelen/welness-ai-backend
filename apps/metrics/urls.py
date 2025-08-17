from django.urls import path
from . import views

app_name = 'metrics'

urlpatterns = [
    path('', views.health_calculator_dashboard, name='dashboard'),
    path('calculator/', views.health_calculator_form, name='calculator_form'),
    path('calculator/<uuid:calculator_id>/', views.calculator_result, name='calculator_result'),
    path('values/', views.metric_values, name='metric_values'),
    path('custom/', views.custom_metrics, name='custom_metrics'),
    path('activity/', views.activity_log, name='activity_log'),
    path('toggle-favorite/', views.toggle_favorite, name='toggle_favorite'),
]
