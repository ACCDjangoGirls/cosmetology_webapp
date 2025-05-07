from django import forms
from .models import Event, Reservation, Review

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = '__all__'
        #widgets are needed for pretty date picking
        widgets = {
            'start_time_and_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'services': forms.CheckboxSelectMultiple()
        }

class UserAppointmentForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['services', 'time_and_date']
        #widgets are needed for pretty date picking
        widgets = {
            'time_and_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'services': forms.CheckboxSelectMultiple()
        }

class AdminAppointmentForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['services', 'time_and_date','professional']
        #widgets are needed for pretty date picking
        widgets = {
            'time_and_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'services': forms.CheckboxSelectMultiple()
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['title', 'text', 'stars', 'event', 'services']
        widgets = {
            'services': forms.CheckboxSelectMultiple(),
        }
        labels = {
            'event': 'Event (optional)',
            'services': 'Services (optional)',
        }