from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import generic, View
from .models import Service, ServiceProfessional, Event, Reservation, Review
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from .forms import EventForm, UserAppointmentForm, AdminAppointmentForm, ReviewForm, ServiceForm
from datetime import date
import random
from django.core.mail import send_mail
from django.conf import settings

# Create your views here.

#https://docs.djangoproject.com/en/5.2/topics/email/
def send_appointment_email(appointment):
    subject = "Your Appointment Confirmation"

    message = (
        f"Hello {appointment.user.username},\n\n"
        f"Your appointment has been confirmed with the following details:\n\n"
        f"Event: {appointment.event.name}\n"
        f"Date: {appointment.time_and_date}\n"
        f"Services: {', '.join(service.name for service in appointment.services.all())}\n"
        f"Assigned Professional: {appointment.professional.name if appointment.professional else 'TBD'}\n\n"
        f"Thank you for choosing our services!\n"
        f"- Cosmetology Team"
    )

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [appointment.user.email],
        fail_silently=False,
    )


class Home(generic.ListView):
    model = Event
    template_name = "core/home_placeholder.html"
    context_object_name = 'events'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['services'] = Service.objects.all()  # Add services manually
        return context

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

        return reverse_lazy('Cosmetology:home_placeholder', kwargs={'pk': self.object.pk})


    
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
    form_class = UserAppointmentForm
    template_name = "core/appointment_create.html"
    success_url = reverse_lazy('Cosmetology:user_appointments')

    #filtering what services show up
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['services'].queryset = Service.objects.filter(event=self.kwargs['event_id'])
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        event_id = self.kwargs.get('event_id') #you use self.kwargs.get to grab an id from a url
        event = get_object_or_404(Event, pk=event_id)
        context['event'] = event

        return context

    def get_initial(self):
        initial = super().get_initial()
        event_id = self.kwargs.get('event_id')
        event = get_object_or_404(Event, pk=event_id)
        initial['time_and_date'] = event.start_time_and_date.date
        return initial

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

        selected_time = form.cleaned_data['time_and_date'] #get the date the user picked
        if Event.objects.filter(pk = event.pk, start_time_and_date__lte = selected_time, end_time__gte=selected_time).exists()==False: #https://www.w3schools.com/django/ref_lookups_lte.php
            form.add_error(None, "Appointment time must be within event start and end time.")
            return self.form_invalid(form)
        
        #!!! do this first instead of directly returning this line because it creates self.object and we need self.object to use the emailing function
        response = super().form_valid(form)
        send_appointment_email(self.object)
        return response
    
class UserAppointmentEdit(LoginRequiredMixin, generic.UpdateView):
    model = Reservation
    #form_class = AppointmentForm
    template_name = "core/appointment_edit.html"
    def get_form_class(self):
        if self.request.user.is_superuser:
            return AdminAppointmentForm
        return UserAppointmentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        event_id = self.kwargs.get('event_id') #you use self.kwargs.get to grab an id from a url
        event = get_object_or_404(Event, pk=event_id)
        context['event'] = event

        return context

    #filtering what services show up
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['services'].queryset = Service.objects.filter(event=self.kwargs['event_id'])
        return form

    def get_queryset(self): #usually in owner.py
        qs = super().get_queryset() #the queryset is the set of appointments that a user can get directed to. We are filtering them in this method.
        if self.request.user.is_superuser:
            return qs #make every appointment available for the admin
        return qs.filter(user=self.request.user) #only make the user's appointments available for the user
    
    def form_valid(self, form): #using form_valid to automatically assign a pro, kinda like how we did with owner.py

        event_id = self.kwargs.get('event_id') #you use self.kwargs.get to grab an id from a url
        event = get_object_or_404(Event, pk=event_id)
        form.instance.event = event #make the selection from the last page apply to the appointment
        
        selected_time = form.cleaned_data['time_and_date'] #get the date the user picked
        if Event.objects.filter(pk = event.pk, start_time_and_date__lte = selected_time, end_time__gte=selected_time).exists()==False: #https://www.w3schools.com/django/ref_lookups_lte.php
            form.add_error(None, "Appointment time must be within event start and end time.")
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
        return Reservation.objects.all().order_by('time_and_date')
    
class Services(generic.ListView): #we will show the details in the list since the model only has 2 fields.
    model = Service
    fields = '__all__'
    template_name = "core/services.html"

class ServiceAdd(LoginRequiredMixin, generic.CreateView):
    model = Service
    template_name = "core/service_add.html"
    success_url = reverse_lazy('Cosmetology:services')  
    form_class = ServiceForm

    def dispatch(self, request, *args, **kwargs): #I believe dispatch is used when you're handling logic BEFORE any other logic
        if not request.user.is_superuser:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs) #If the user is a superuser, this line calls the original dispatch() method from the parent class

class ServiceDelete(LoginRequiredMixin, generic.DeleteView):
    model = Service
    template_name = "core/service_delete.html"
    success_url = reverse_lazy('Cosmetology:services')
    
    def dispatch(self, request, *args, **kwargs): #I believe dispatch is used when you're handling logic BEFORE any other logic
        if not request.user.is_superuser:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs) #If the user is a superuser, this line calls the original dispatch() method from the parent class


class ServiceEdit(LoginRequiredMixin, generic.UpdateView):
    model = Service
    fields = '__all__'
    template_name = "core/service_edit.html"
    form_class = ServiceForm

    def dispatch(self, request, *args, **kwargs): #I believe dispatch is used when you're handling logic BEFORE any other logic
        if not request.user.is_superuser:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs) #If the user is a superuser, this line calls the original dispatch() method from the parent class
    
    def get_success_url(self): #success url doesn't work when you want to pass the primary key
        return reverse_lazy('Cosmetology:services')

class ServiceProviders(generic.ListView):
    model = ServiceProfessional
    template_name = "core/service_providers.html"

class ServiceProviderAdd(LoginRequiredMixin, generic.CreateView):
    model = ServiceProfessional
    template_name = "core/service_provider_add.html"
    success_url = reverse_lazy('Cosmetology:service_providers')  
    fields = '__all__'

    def dispatch(self, request, *args, **kwargs): #I believe dispatch is used when you're handling logic BEFORE any other logic
        if not request.user.is_superuser:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs) #If the user is a superuser, this line calls the original dispatch() method from the parent class

class ServiceProviderDelete(LoginRequiredMixin, generic.DeleteView):
    model = ServiceProfessional
    template_name = "core/service_provider_delete.html"
    success_url = reverse_lazy('Cosmetology:service_providers')  
    
    def dispatch(self, request, *args, **kwargs): #I believe dispatch is used when you're handling logic BEFORE any other logic
        if not request.user.is_superuser:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs) #If the user is a superuser, this line calls the original dispatch() method from the parent class


class ServiceProviderUpdate(LoginRequiredMixin, generic.UpdateView):
    model = ServiceProfessional
    template_name = "core/service_provider_edit.html"
    fields = '__all__'

    def dispatch(self, request, *args, **kwargs): #I believe dispatch is used when you're handling logic BEFORE any other logic
        if not request.user.is_superuser:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs) #If the user is a superuser, this line calls the original dispatch() method from the parent class
    
    def get_success_url(self):
        return reverse_lazy('Cosmetology:service_providers')
class Reviews(generic.ListView):
    model = Review
    template_name = "core/reviews.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['form'] = ReviewForm()

        return context


class ReviewAddView(LoginRequiredMixin, View):
    def get(self,request):
        return redirect(reverse('Cosmetology:reviews'))
    
    def post(self, request) :
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False) 
            review.user = self.request.user
            review.username = self.request.user.username
            review.save() 
            form.save_m2m() #apparently needed if you are saving a form with many to many relationships.
        return redirect(reverse('Cosmetology:reviews'))


class ReviewDeleteView(LoginRequiredMixin, View):
    def get(self, request):
        return redirect(reverse('Cosmetology:reviews'))

    def post(self, request, pk):
        review = get_object_or_404(Review, id=pk)
        if review.user == request.user or request.user.is_superuser:
            review.delete()
        return redirect(reverse('Cosmetology:reviews'))
