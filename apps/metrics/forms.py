from django import forms
from django.utils import timezone
from datetime import date
from .models import HealthCalculator, Metric, MetricValue


class HealthCalculatorForm(forms.ModelForm):
    """Form for health calculator input"""
    
    class Meta:
        model = HealthCalculator
        fields = [
            'weight_kg', 
            'height_cm', 
            'body_fat_percentage', 
            'gender', 
            'activity_level',
            'activity_hours_per_week',
            'notes'
        ]
        widgets = {
            'weight_kg': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter weight in kg',
                'step': '0.1',
                'min': '20',
                'max': '300'
            }),
            'height_cm': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter height in cm',
                'step': '0.1',
                'min': '100',
                'max': '250'
            }),
            'body_fat_percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter body fat percentage',
                'step': '0.1',
                'min': '0',
                'max': '50'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-control'
            }),
            'activity_level': forms.Select(attrs={
                'class': 'form-control'
            }),
            'activity_hours_per_week': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Hours of exercise per week',
                'step': '0.5',
                'min': '0',
                'max': '50'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes (optional)'
            }),
        }
    
    def clean_weight_kg(self):
        weight = self.cleaned_data.get('weight_kg')
        if weight and (weight < 20 or weight > 300):
            raise forms.ValidationError('Weight must be between 20 and 300 kg')
        return weight
    
    def clean_height_cm(self):
        height = self.cleaned_data.get('height_cm')
        if height and (height < 100 or height > 250):
            raise forms.ValidationError('Height must be between 100 and 250 cm')
        return height
    
    def clean_body_fat_percentage(self):
        body_fat = self.cleaned_data.get('body_fat_percentage')
        if body_fat and (body_fat < 0 or body_fat > 50):
            raise forms.ValidationError('Body fat percentage must be between 0 and 50%')
        return body_fat


class MetricValueForm(forms.ModelForm):
    """Form for metric values (measurements)"""
    
    class Meta:
        model = MetricValue
        fields = ['metric', 'value', 'measurement_type', 'status', 'notes', 'source']
        widgets = {
            'metric': forms.Select(attrs={
                'class': 'form-control'
            }),
            'value': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'placeholder': 'Enter value'
            }),
            'measurement_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Notes (optional)'
            }),
            'source': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Source (e.g., Home Scale, Lab Corp)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter metrics to show only active ones
        self.fields['metric'].queryset = Metric.objects.filter(is_active=True).order_by('type', 'name')
    
    def clean_value(self):
        value = self.cleaned_data.get('value')
        metric = self.cleaned_data.get('metric')
        
        if value is not None and metric:
            # Check against metric's min/max values if defined
            if metric.min_value is not None and value < metric.min_value:
                raise forms.ValidationError(f'Value must be at least {metric.min_value} {metric.unit}')
            if metric.max_value is not None and value > metric.max_value:
                raise forms.ValidationError(f'Value must be at most {metric.max_value} {metric.unit}')
        
        return value





class CustomMetricForm(forms.Form):
    """Form for creating custom metrics"""
    name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter metric name (e.g., Custom Blood Pressure)'
        })
    )
    type = forms.ChoiceField(
        choices=Metric.METRIC_TYPES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    unit = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Unit (e.g., mg/dL, pmol/L, custom unit)'
        })
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Description of what this metric measures (optional)'
        })
    )
    min_value = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Minimum acceptable value (optional)',
            'step': '0.1'
        })
    )
    max_value = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Maximum acceptable value (optional)',
            'step': '0.1'
        })
    )
    reference_range = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Normal range (e.g., 70-100) (optional)'
        })
    )


class QuickCalculatorForm(forms.Form):
    """Quick calculator form for real-time calculations"""
    weight_kg = forms.FloatField(
        label='Weight (kg)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '97',
            'step': '0.1',
            'min': '20',
            'max': '300'
        })
    )
    height_cm = forms.FloatField(
        label='Height (cm)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '192',
            'step': '0.1',
            'min': '100',
            'max': '250'
        })
    )
    body_fat_percentage = forms.FloatField(
        label='Body Fat (%)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '20',
            'step': '0.1',
            'min': '0',
            'max': '50'
        })
    )
    age_years = forms.IntegerField(
        label='Age (years)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '41',
            'min': '10',
            'max': '120'
        })
    )
    gender = forms.ChoiceField(
        label='Gender',
        choices=HealthCalculator.GENDER_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    activity_level = forms.ChoiceField(
        label='Activity Level',
        choices=HealthCalculator.ACTIVITY_LEVELS,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
