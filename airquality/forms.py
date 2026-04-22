from django import forms
from .models import City, AirQualityData, Pollutant, Evaluation, Country, MeasurementStation


class CityForm(forms.ModelForm):
    class Meta:
        model = City
        fields = ['name', 'country', 'latitude', 'longitude', 'population', 'description', 'image_url']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class AirQualityDataForm(forms.ModelForm):
    class Meta:
        model = AirQualityData
        fields = ['station', 'pollutant', 'value', 'unit', 'measurement_date', 'is_valid']
        widgets = {
            'measurement_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['measurement_date'].input_formats = ['%Y-%m-%dT%H:%M']


class PollutantForm(forms.ModelForm):
    class Meta:
        model = Pollutant
        fields = ['name', 'symbol', 'description', 'limit_oms', 'limit_eu', 'unit']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class EvaluationForm(forms.ModelForm):
    class Meta:
        model = Evaluation
        fields = ['author_name', 'rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Votre commentaire...'}),
            'author_name': forms.TextInput(attrs={'placeholder': 'Votre nom'}),
        }
        labels = {
            'author_name': 'Votre nom',
            'rating': 'Note (1 à 5)',
            'comment': 'Commentaire',
        }
