from django.contrib import admin
from .models import Goal, BodyMeasurement

# Register your models here.
admin.site.register(Goal)
admin.site.register(BodyMeasurement)
