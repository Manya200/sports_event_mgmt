from django import forms
from .models import Event , Venue

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'name', 
            'description', 
            'start_date', 
            'end_date', 
            'venue', 
            'registration_fee', 
            'ticket_price',
        ]
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['venue'].queryset = Venue.objects.all()

class EventUpdateForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'name', 
            'description', 
            'start_date', 
            'end_date', 
            'venue', 
            'registration_fee', 
            'ticket_price',
        ]
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class VenueForm(forms.ModelForm):
    class Meta:
        model = Venue
        fields = ['name', 'address', 'capacity'] 