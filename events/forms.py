from django import forms
from .models import Event , Venue
from django.contrib.auth.models import User

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
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()  # This ensures we use the default User model

class CustomUserCreationForm(UserCreationForm):
    ROLE_CHOICES = [
        # ('admin', 'Admin'),
        ('event_organizer', 'Event Organizer'),
        ('user', 'User'),
        ('venue_manager', 'Venue Manager'),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True, label="Select Role")
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2", "role"]
