from django import forms
from .models import Event

# Form for creating and editing Event records.
# This uses Django's ModelForm to build form fields from the Event model.
class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'category', 'date', 'time', 'location', 'max_participants']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'max_participants': forms.NumberInput(attrs={'type': 'number', 'min': '1', 'placeholder': 'Leave empty for unlimited'}),
        }


from .models import Ticket, Booking, Venue

# Form for booking a ticket. It only needs the ticket type and quantity.
class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['ticket', 'quantity']


# Form for creating or editing a Venue.
class VenueForm(forms.ModelForm):
    class Meta:
        model = Venue
        fields = ['name', 'capacity', 'location', 'is_available']


from .models import Registration

# Form for collecting registration details from a user.
class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = ['full_name', 'email', 'phone', 'address']
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Your full name'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Your phone number'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Your email address'}),
            'address': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Your address (optional)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['full_name'].required = True
        self.fields['phone'].required = True
        self.fields['email'].required = False
        self.fields['address'].required = False
