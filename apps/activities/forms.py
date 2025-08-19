from django import forms
from datetime import date
from .models import Activity, ActivityRecord, Exercise, ActivityExercise
from django.utils import timezone


class ActivityForm(forms.ModelForm):
    """Form for creating and editing planned activities"""
    
    class Meta:
        model = Activity
        fields = [
            'name',
            'activity_type',
            'duration_hours',
            'is_scheduled',
            'start_date',
            'end_date',
            'start_time',
            'recurrence_type',
            'recurrence_until',
            'recurrence_days',
            'notes',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500',
                'placeholder': 'Enter activity name (optional)'
            }),
            'activity_type': forms.Select(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500'
            }),
            'duration_hours': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500',
                'step': '0.25',
                'min': '0.25'
            }),
            'is_scheduled': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500',
                'type': 'date'
            }),
            'start_time': forms.TimeInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500',
                'type': 'time'
            }),
            'recurrence_type': forms.Select(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500'
            }),
            'recurrence_until': forms.DateInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500',
                'type': 'date'
            }),
            'recurrence_days': forms.TextInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500',
                'placeholder': 'e.g., mon,tue,thu,fri'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500',
                'rows': 3,
                'placeholder': 'Additional notes about this activity...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default start date to today if not provided
        if not self.instance.pk and not self.data.get('start_date'):
            self.fields['start_date'].initial = timezone.now().date()
        
        # Set default start time to current time if not provided
        if not self.instance.pk and not self.data.get('start_time'):
            self.fields['start_time'].initial = timezone.now().time()
    
    def clean(self):
        cleaned_data = super().clean()
        is_scheduled = cleaned_data.get('is_scheduled')
        start_date = cleaned_data.get('start_date')
        start_time = cleaned_data.get('start_time')
        recurrence_type = cleaned_data.get('recurrence_type')
        recurrence_until = cleaned_data.get('recurrence_until')
        
        # If scheduled, require start_date
        if is_scheduled and not start_date:
            raise forms.ValidationError("Start date is required for scheduled activities.")
        
        # If recurrence is set, require recurrence_until
        if recurrence_type and recurrence_type != 'none' and not recurrence_until:
            raise forms.ValidationError("Recurrence end date is required for recurring activities.")
        
        # Ensure recurrence_until is after start_date
        if start_date and recurrence_until and recurrence_until <= start_date:
            raise forms.ValidationError("Recurrence end date must be after start date.")
        
        return cleaned_data


class ActivityRecordForm(forms.ModelForm):
    """Form for logging activities (both planned and unplanned)"""
    
    # For unplanned activities
    activity_name = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500',
            'placeholder': 'Activity name (for unplanned activities)'
        })
    )
    activity_type_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500',
            'placeholder': 'Activity type (e.g., running, strength_training)'
        })
    )
    duration_hours = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500',
            'step': '0.25',
            'min': '0.25',
            'placeholder': 'Duration in hours'
        })
    )
    
    class Meta:
        model = ActivityRecord
        fields = [
            'activity',
            'date',
            'start_time',
            'end_time',
            'notes',
        ]
        widgets = {
            'activity': forms.Select(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500'
            }),
            'date': forms.DateInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500',
                'type': 'date'
            }),
            'start_time': forms.TimeInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500',
                'type': 'time'
            }),
            'end_time': forms.TimeInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500',
                'type': 'time'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500',
                'rows': 3,
                'placeholder': 'Notes about this activity session...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Set default date to today if not provided
        if not self.instance.pk and not self.data.get('date'):
            self.fields['date'].initial = timezone.now().date()
        
        # Filter activities by user if provided
        if user:
            self.fields['activity'].queryset = Activity.objects.filter(user=user, is_scheduled=True)
        
        # Make activity field optional for unplanned activities
        self.fields['activity'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        activity = cleaned_data.get('activity')
        activity_name = cleaned_data.get('activity_name')
        activity_type_name = cleaned_data.get('activity_type_name')
        duration_hours = cleaned_data.get('duration_hours')
        
        # Either activity (planned) or activity_name + activity_type_name + duration_hours (unplanned) must be provided
        if not activity and not (activity_name and activity_type_name and duration_hours):
            raise forms.ValidationError(
                "Either select a planned activity or provide activity name, type, and duration for unplanned activities."
            )
        
        # If activity is selected, ignore unplanned fields
        if activity:
            cleaned_data['activity_name'] = None
            cleaned_data['activity_type_name'] = None
            cleaned_data['duration_hours'] = None
        
        return cleaned_data


class ExerciseForm(forms.ModelForm):
    """Form for creating exercises"""
    
    class Meta:
        model = Exercise
        fields = [
            'name',
            'description',
            'category',
            'muscle_groups',
            'difficulty_level',
            'equipment_needed',
            'calories_per_hour_per_kg',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500'
            }),
            'description': forms.Textarea(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500',
                'rows': 3
            }),
            'category': forms.Select(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500'
            }),
            'muscle_groups': forms.TextInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500',
                'placeholder': 'e.g., chest, triceps, shoulders'
            }),
            'difficulty_level': forms.Select(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500'
            }),
            'equipment_needed': forms.TextInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500',
                'placeholder': 'e.g., barbell, dumbbells, bench'
            }),
            'calories_per_hour_per_kg': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500',
                'step': '0.1'
            }),
        }


class ActivityExerciseForm(forms.ModelForm):
    """Form for adding exercises to activities"""
    exercise_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500',
            'placeholder': 'Type exercise name...'
        })
    )
    
    class Meta:
        model = ActivityExercise
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500',
                'rows': 4,
                'placeholder': 'Describe your workout details: sets, reps, weight, distance, technique, or any other information...'
            })
        }
