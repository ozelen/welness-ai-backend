from django.contrib import admin
from .models import HealthCalculator, Metric, MetricValue, UserMetricFavorite

@admin.register(HealthCalculator)
class HealthCalculatorAdmin(admin.ModelAdmin):
    list_display = ['user', 'weight_kg', 'height_cm', 'body_fat_percentage', 'activity_level', 'created_at']
    list_filter = ['activity_level', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Body Measurements', {
            'fields': ('weight_kg', 'height_cm', 'body_fat_percentage')
        }),
        ('Activity Level', {
            'fields': ('activity_level',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Calculate and store metrics when calculator is saved
        from .services import HealthCalculatorService
        HealthCalculatorService.calculate_and_store_metrics(obj)

@admin.register(Metric)
class MetricAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'unit', 'is_calculated', 'is_active', 'metric_id']
    list_filter = ['type', 'is_calculated', 'is_active']
    search_fields = ['name', 'description', 'metric_id']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'type', 'unit', 'description', 'metric_id')
        }),
        ('Display Settings', {
            'fields': ('icon', 'color', 'is_active')
        }),
        ('Calculated Metrics', {
            'fields': ('is_calculated', 'calculation_formula'),
            'classes': ('collapse',)
        }),
        ('Validation', {
            'fields': ('min_value', 'max_value', 'reference_range'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(MetricValue)
class MetricValueAdmin(admin.ModelAdmin):
    list_display = ['user', 'metric', 'value', 'measurement_type', 'timestamp', 'source']
    list_filter = ['measurement_type', 'timestamp', 'metric__type']
    search_fields = ['user__username', 'metric__name', 'notes', 'source']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'metric', 'value', 'measurement_type')
        }),
        ('Additional Information', {
            'fields': ('source', 'notes', 'timestamp')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )



@admin.register(UserMetricFavorite)
class UserMetricFavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'metric', 'created_at']
    list_filter = ['created_at', 'metric__type']
    search_fields = ['user__username', 'metric__name']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('User and Metric', {
            'fields': ('user', 'metric')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
