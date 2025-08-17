from django.apps import AppConfig


class MetricsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'metrics'
    verbose_name = 'Health Metrics'
    
    def ready(self):
        """Import signals when the app is ready"""
        try:
            import metrics.signals  # noqa
        except ImportError:
            pass
