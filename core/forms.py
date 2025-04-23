from django import forms
from .models import Event, Reservation

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = '__all__'
        #widgets are needed for pretty date picking
        widgets = {
            'start_time_and_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['event', 'services', 'time_and_date']
        #widgets are needed for pretty date picking
        widgets = {
            'time_and_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
