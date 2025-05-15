from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

# Create your models here.

class Service(models.Model):
    name = models.CharField(max_length=200)
    service_description = models.CharField(max_length=200)
    def __str__(self):
        return self.name

class ServiceProfessional(models.Model):
    name = models.CharField(max_length=200)

    services = models.ManyToManyField(Service)
    def __str__(self):
        return self.name

class Event(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    start_time_and_date = models.DateTimeField()
    event_location = models.CharField(max_length=200)
    end_time = models.DateTimeField()
    services = models.ManyToManyField(Service)

    #removed service relationship
    def __str__(self):
        return self.name

class Reservation(models.Model):
    username = models.CharField(max_length=200)
    time_and_date = models.DateTimeField()

    #each reservation belongs to an event, an event can have many reservations
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    professional = models.ForeignKey(ServiceProfessional, on_delete=models.CASCADE, null=True, blank=True) #just in case
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    services = models.ManyToManyField(Service)

    def __str__(self):
       return f"Reservation for {self.event} by {self.user}"

class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    username = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    text = models.CharField(max_length=200)
    time_and_date = models.DateTimeField(auto_now=True)

    event = models.ForeignKey(Event, null=True, blank=True, on_delete=models.SET_NULL)
    services = models.ManyToManyField(Service, blank=True)

    #https://www.youtube.com/watch?v=kc47J3qoLU4 ignore, putting it here in case i need to come back to it
    STAR_CHOICES = [
        (1, '⭐'), #1 gets stored in the database, the star is what the user sees
        (2, '⭐⭐'),
        (3, '⭐⭐⭐'),
        (4, '⭐⭐⭐⭐'),
        (5, '⭐⭐⭐⭐⭐'),
    ]

    stars = models.IntegerField(choices=STAR_CHOICES)
    def __str__(self):
       return f"{self.title}"
