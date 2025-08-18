from django import forms
from datetime import date
from .models import Activity, ActivityRecord


class ActivityRecordForm(forms.ModelForm):
    """Form for logging actual activities"""
    
    class Meta:
        model = ActivityRecord
        fields = [
            'activity_type', 
            'duration_hours', 
            'date',
            'notes'
        ]
        widgets = {
            'activity_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'duration_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Duration in hours (e.g., 1.5 for 1 hour 30 minutes)',
                'step': '0.25',
                'min': '0.25',
                'max': '24'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Activity notes (optional)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default date to today
        if not self.instance.pk:
            self.fields['date'].initial = date.today()
    
    def clean_duration_hours(self):
        duration = self.cleaned_data.get('duration_hours')
        if duration and (duration < 0.25 or duration > 24):
            raise forms.ValidationError('Duration must be between 0.25 and 24 hours')
        return duration


class ActivityForm(forms.ModelForm):
    """Form for planning activities"""
    
    class Meta:
        model = Activity
        fields = [
            'activity_type', 
            'duration_hours', 
            'date',
            'notes'
        ]
        widgets = {
            'activity_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'duration_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Planned duration in hours (e.g., 1.5 for 1 hour 30 minutes)',
                'step': '0.25',
                'min': '0.25',
                'max': '24'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Planning notes (optional)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default date to today
        if not self.instance.pk:
            self.fields['date'].initial = date.today()
    
    def clean_duration_hours(self):
        duration = self.cleaned_data.get('duration_hours')
        if duration and (duration < 0.25 or duration > 24):
            raise forms.ValidationError('Duration must be between 0.25 and 24 hours')
        return duration
