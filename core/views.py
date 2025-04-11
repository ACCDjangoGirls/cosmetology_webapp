from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import generic, View
from .models import Service, ServiceProfessional, Event, Reservation, 
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.

class EventDetail(generic.DetailView):
    model = Event

class EventAdd(generic.CreateView):
    model = Event

class EventDelete(generic.DeleteView):
    model = Event

class EventEdit(generic.EditView):
    model = Event