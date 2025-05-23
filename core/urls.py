from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = "Cosmetology"
urlpatterns = [
    path("", views.Home.as_view(), name="index"), #it is going to list events in the calendar
    path('accounts/logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path("event_detail/<pk>", views.EventDetail.as_view(), name="event_detail"), #upon clicking event from calendar


    #admin only
    path("event_add", views.EventAdd.as_view(), name="event_add"), 
    path("event_delete/<pk>", views.EventDelete.as_view(), name="event_delete"),
    path("event_edit/<pk>", views.EventEdit.as_view(), name="event_edit"),

    path("services", views.Services.as_view(), name="services"),
    path("service_add", views.ServiceAdd.as_view(), name="service_add"),
    path("service_delete/<pk>", views.ServiceDelete.as_view(), name="service_delete"),
    path("service_edit/<pk>", views.ServiceEdit.as_view(), name="service_edit"),

    #services are assigned to events in the event CRUD

    #path("contact", views.Contact.as_view(), name="contact"),

    path("user_appointments", views.UserAppointments.as_view(), name="user_appointments"), #list their appts.
    path("user_appointment_cancel/<pk>", views.UserAppointmentCancel.as_view(), name="user_appointment_cancel"), 
    path("user_appointment_pick_event_create", views.SelectEventCreateView.as_view(), name="user_appointment_pick_event_create"),
    path("user_appointment_pick_event_update/<pk>", views.SelectEventUpdateView.as_view(), name="user_appointment_pick_event_update"),
    path("user_appointment_add/<int:event_id>", views.UserAppointmentAdd.as_view(), name="user_appointment_add"), #name other id's for clarity
    path('user_appointment/<int:event_id>/edit/<pk>/', views.UserAppointmentEdit.as_view(), name='user_appointment_update'),
    
    #admin only
    path("admin_user_appointments", views.AdminUserAppointments.as_view(), name="admin_user_appointments"), #list ALL apts.

    #admin only
    path("service_providers", views.ServiceProviders.as_view(), name="service_providers"), 
    path("service_provider_add", views.ServiceProviderAdd.as_view(), name="service_provider_add"), 
    path("service_provider_update/<pk>", views.ServiceProviderUpdate.as_view(), name="service_provider_edit"),
    path("service_provider_delete/<pk>", views.ServiceProviderDelete.as_view(), name="service_provider_delete"),

    path("reviews", views.Reviews.as_view(), name="reviews"),
    path("review_add", views.ReviewAddView.as_view(), name="review_add"),
    path("review_delete/<pk>", views.ReviewDeleteView.as_view(), name="review_delete"),
]
