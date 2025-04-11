from django.urls import path

from . import views

app_name = "Cosmetology"
urlpatterns = [
    path("", views.Home.as_view(), name="index"), #it is going to list events in the calendar
    path("event_detail/<pk>", views.EventDetail.as_view(), name="event_detail"), #upon clicking event from calendar

    #admin only
    path("event_add", views.EventAdd.as_view(), name="event_add"), 
    path("event_delete/<pk>", views.EventDelete.as_view(), name="event_delete"),
    path("event_edit/<pk>", views.EventEdit.as_view(), name="event_edit"),

    path("services", views.Services.as_view(), name="services"),
    path("service_add/<pk>", views.ServiceAdd.as_view(), name="service_add"),
    path("service_delete/<pk>", views.ServiceDelete.as_view(), name="service_delete"),
    path("service_edit/<pk>", views.ServiceEdit.as_view(), name="service_edit"),

    #admin only
    path("event_service_add", views.EventServiceAdd.as_view(), name="event_service_add"), #plus icon next to calendar
    path("event_service_update/<pk>", views.EventServiceUpdate.as_view(), name="event_service_update"), #edit icon on each calendar tile
    path("event_service_delete/<pk>", views.EventServiceDelete.as_view(), name="event_service_delete"), #same but delete

    path("contact", views.Contact.as_view(), name="contact"),

    path("user_appointments", views.UserAppointments.as_view(), name="user_appointments"), #list their appts.
    #generic delete, this will be seen upon canceling in the appointments template (linked to in home)
    path("user_appointment_cancel/<pk>", views.UserAppointmentCancel.as_view(), name="user_appointment_cancel"), 
    path("user_appointment_add", views.UserAppointmentAdd.as_view(), name="user_appointment_add"), 
    path("user_appointment_update/<pk>", views.UserAppointmentUpdate.as_view(), name="user_appointment_update"),

    #admin and user can see this, seen after creating an appt or after clicking on one from the 
    #user_appointments url or admin_appointments url
    path("appointment_detail/<pk>", views.AppointmentDetail.as_view(), name="appointment_detail"), 
    

    path("admin_appointments", views.AdminAppointments.as_view(), name="admin_appointments"), #list ALL apts.
    path("admin_appointment_add", views.AdminAppointmentAdd.as_view(), name="admin_appointment_add"),
    path("admin_appointment_update/<pk>", views.AdminAppointmentUpdate.as_view(), name="admin_appointment_update"),
    path("admin_appointment_delete/<pk>", views.AdminAppointmentDelete.as_view(), name="admin_appointment_delete"),

    #admin only
    path("service_providers", views.ServiceProviders.as_view(), name="service_providers"), 
    path("service_provider_add", views.ServiceProviderAdd.as_view(), name="service_provider_add"), 
    path("service_provider_update/<pk>", views.ServiceProviderUpdate.as_view(), name="service_provider_update"),
    path("service_provider_delete/<pk>", views.ServiceProviderDelete.as_view(), name="service_provider_delete"),

    
]