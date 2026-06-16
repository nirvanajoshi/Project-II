from django import forms
from .models import Event

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'category', 'date', 'time', 'location']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }


from .models import Ticket, Booking, Venue


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['ticket', 'quantity']


class VenueForm(forms.ModelForm):
    class Meta:
        model = Venue
        fields = ['name', 'capacity', 'location', 'is_available']


from .models import Registration


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = ['full_name', 'email', 'phone', 'address']
