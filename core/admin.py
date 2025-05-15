from django.contrib import admin
from .models import Service, ServiceProfessional, Event, Reservation, Review
# Register your models here.
admin.site.register(Service)
admin.site.register(ServiceProfessional)
admin.site.register(Event)
admin.site.register(Reservation)
admin.site.register(Review)
