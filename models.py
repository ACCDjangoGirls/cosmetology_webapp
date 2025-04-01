from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

# Create your models here.

#add stuff to user model

class Reservation(models.Model):
    username = models.CharField(max_length=200)
    time_and_date = models.DateTimeField(auto_now=True) 

    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
       return f"Reservation for {self.event} by {self.user}"

class Service(models.Model):
    name = models.CharField(max_length=200)
    service_description = models.CharField(max_length=200)
    def __str__(self):
        return self.name


class Event(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    start_time_and_date = models.DateTimeField()
    event_location = models.CharField(max_length=200)
    end_time = models.DateTimeField()

    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    def __str__(self):
        return self.name


class ServiceProfessional(models.Model):
    name = models.CharField(max_length=200)
    class_period = models.CharField(max_length=200)

    service = models.ManyToManyField(Service)
    def __str__(self):
        return self.name

