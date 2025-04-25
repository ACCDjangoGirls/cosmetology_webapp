from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import generic, View
from .models import Service, ServiceProfessional, Event, Reservation
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from .forms import EventForm, AppointmentForm
import random

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
    
    def dispatch(self, request, *args, **kwargs): #I believe dispatch is used when you're handling logic BEFORE any other logic
        if not request.user.is_superuser:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs) #If the user is a superuser, this line calls the original dispatch() method from the parent class


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
    
class UserAppointments(LoginRequiredMixin, generic.ListView):
    model = Reservation
    template_name = "core/user_appointments.html"

    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user)
    
class SelectEventCreateView(LoginRequiredMixin, View): #cant use generic here since we are not CRUDing, only grabbing an event id and trying to pass it down to the next view
    def get(self, request):
        events = Event.objects.all()
        return render(request, 'core/event_select.html', {'events': events})

    def post(self, request):
        event_id = request.POST.get('event') #get that event id
        return redirect('Cosmetology:user_appointment_add', event_id=event_id) #go to the appointment_add view and provide the event to the view for filtering logic
    
class SelectEventUpdateView(LoginRequiredMixin, View): #seems inneficient but I don't know how else to do this
    def get(self, request, pk):
        events = Event.objects.all()
        return render(request, 'core/event_select.html', {'events': events})

    def post(self, request, pk):
        event_id = request.POST.get('event')
        return redirect('Cosmetology:user_appointment_update', event_id=event_id, pk=pk) 
    
class UserAppointmentAdd(LoginRequiredMixin, generic.CreateView):
    model = Reservation
    form_class = AppointmentForm
    template_name = "core/appointment_create.html"
    success_url = reverse_lazy('Cosmetology:user_appointments')

    #filtering what services show up
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['services'].queryset = Service.objects.filter(event=self.kwargs['event_id'])
        return form


    def form_valid(self, form): #using form_valid to automatically assign a pro, kinda like how we did with owner.py
        user = self.request.user #get the user
        form.instance.user = user #assign to the form, like owner.py
        form.instance.username = user.username #assign username

        event_id = self.kwargs.get('event_id') #you use self.kwargs.get to grab an id from a url
        event = get_object_or_404(Event, pk=event_id)
        form.instance.event = event #make the selection from the last page apply to the appointment

        selected_services = form.cleaned_data['services'] #this is how u get the clean data in a form valid function 

        all_pros = list(ServiceProfessional.objects.all()) #query all proffessionals 
        random.shuffle(all_pros) #gives equal chance for each pro to get selected
        for professional in all_pros: #get all the proffessionals
            has_all_services = True #see whether they have that service
            for service in selected_services: #check each service
                if service not in professional.services.all(): #and see if it is in the proffessional's list of services
                    has_all_services = False
                    break #get out

            if has_all_services == True: #if they do, assign them and stop the loop
                form.instance.professional = professional
                break
        else: #show error if no proffessional has all those services
            form.add_error(None, "No professional offers all selected services.") #add_error allows you to specify what error to show
            return self.form_invalid(form)

        return super().form_valid(form)
    
class UserAppointmentEdit(LoginRequiredMixin, generic.UpdateView):
    model = Reservation
    form_class = AppointmentForm
    template_name = "core/appointment_edit.html"

    #filtering what services show up
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['services'].queryset = Service.objects.filter(event=self.kwargs['event_id'])
        return form

    def get_queryset(self): #usually in owner.py
        qs = super().get_queryset() #the queryset is the set of appointments that a user can get directed to. We are filtering them here.
        if self.request.user.is_superuser:
            return qs #make every appointment available for the admin
        return qs.filter(user=self.request.user) #only make the user's appointments available for the user
    
    def form_valid(self, form): #using form_valid to automatically assign a pro, kinda like how we did with owner.py

        event_id = self.kwargs.get('event_id') #you use self.kwargs.get to grab an id from a url
        event = get_object_or_404(Event, pk=event_id)
        form.instance.event = event #make the selection from the last page apply to the appointment


        selected_services = form.cleaned_data['services'] #this is how u get the clean data in a form valid function 
        all_pros = list(ServiceProfessional.objects.all()) #query all proffessionals 
        random.shuffle(all_pros) #gives equal chance for each pro to get selected
        for professional in all_pros: #get all the proffessionals
            has_all_services = True #see whether they have that service
            for service in selected_services: #check each service
                if service not in professional.services.all(): #and see if it is in the proffessional's list of services
                    has_all_services = False
                    break #get out

            if has_all_services == True: #if they do, assign them and stop the loop
                form.instance.professional = professional
                break
        else: #show error if no proffessional has all those services
            form.add_error(None, "No professional offers all selected services.") #add_error allows you to specify what error to show
            return self.form_invalid(form)

        return super().form_valid(form)
    
    def get_success_url(self): #success url doesn't work when you want to pass the primary key
        if self.request.user.is_superuser:
            return reverse_lazy('Cosmetology:admin_user_appointments')
        else:
            return reverse_lazy('Cosmetology:user_appointments')
    

class UserAppointmentCancel(LoginRequiredMixin, generic.DeleteView):
    model = Reservation
    template_name = "core/appointment_cancel.html"
    def get_success_url(self): #can't use success_url because I want to have an if statement that uses self.request
        if self.request.user.is_superuser:
            return reverse_lazy('Cosmetology:admin_user_appointments')
        else:
            return reverse_lazy('Cosmetology:user_appointments')

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_superuser:
            return qs
        return qs.filter(user=self.request.user)

    
class AdminUserAppointments(LoginRequiredMixin, generic.ListView):
    model = Reservation
    template_name = "core/admin_user_appointments.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Reservation.objects.all()