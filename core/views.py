from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import generic, View
from .models import Service, ServiceProfessional, Event, Reservation
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from .forms import EventForm

# Create your views here.

class Home(generic.ListView):
    model = Event
    template_name = "core/home_placeholder.html"

class EventDetail(generic.DetailView):
    model = Event
    template_name = "core/event_detail.html"

class EventAdd(LoginRequiredMixin, generic.CreateView):
    model = Event
    template_name = "core/event_add.html"
    form_class = EventForm
    success_url = reverse_lazy('Cosmetology:index')  

    def dispatch(self, request, *args, **kwargs): #I believe dispatch is used when you're handling logic BEFORE any other logic
        if not request.user.is_superuser:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs) #If the user is a superuser, this line calls the original dispatch() method from the parent class

class EventDelete(LoginRequiredMixin, generic.DeleteView):
    model = Event
    template_name = "core/event_delete.html"

class EventEdit(LoginRequiredMixin, generic.UpdateView):
    model = Event
    form_class = EventForm
    template_name = "core/event_edit.html"

    def dispatch(self, request, *args, **kwargs): #I believe dispatch is used when you're handling logic BEFORE any other logic
        if not request.user.is_superuser:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs) #If the user is a superuser, this line calls the original dispatch() method from the parent class
    
    def get_success_url(self): #success url doesn't work when you want to pass the primary key
        return reverse_lazy('Cosmetology:event_detail', kwargs={'pk': self.object.pk})