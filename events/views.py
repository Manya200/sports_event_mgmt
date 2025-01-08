from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.http import HttpResponse
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from .models import Event
from django.shortcuts import render, get_object_or_404, redirect
from .models import Event, EventRegistration ,RegisteredParticipant, EventViewer
from django.contrib import messages

def homepage(request):
    return render(request, 'homepage.html')

# # Defineing a view to handle the login functionality
# @login_required
# def dashboard(request):
#     user = request.user

#     if user.groups.filter(name='Event Organizer').exists():
#         return redirect('event_organizer_dashboard')
#     elif user.groups.filter(name='Venue Manager').exists():
#         return redirect('venue_manager_dashboard')
#     elif user.groups.filter(name='User (Participant)').exists():
#         return redirect('participant_dashboard')
#     else:
#         return render(request, 'error.html', {'message': 'Unauthorized access!'})

# # Defineing a view to handle the login functionality of participant
# @login_required
# def participant_dashboard(request):
#     return render(request, 'participant_dashboard.html')

# # Defineing a view to handle the login functionality of event organizer.
# @login_required
# def event_organizer_dashboard(request):
#     return render(request, 'event_organizer_dashboard.html')

# # Defineing a view to handle the login functionality of venue manager.
# @login_required
# def venue_manager_dashboard(request):
#     return render(request, 'venue_manager_dashboard.html')

# from django.contrib.auth.views import LoginView
# from django.urls import reverse_lazy

# class CustomLoginView(LoginView):
#     template_name = 'registration/login.html'

#     def get_success_url(self):
#         return reverse_lazy('dashboard')

# Custom Login View
class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def get_success_url(self):
        user = self.request.user
        # Redirect based on user group
        if user.groups.filter(name='Event Organizer').exists():
            return reverse_lazy('event_organizer_dashboard')  # Event Organizer Dashboard
        elif user.groups.filter(name='Venue Manager').exists():
            return reverse_lazy('venue_manager_dashboard')  # Venue Manager Dashboard
        elif user.groups.filter(name='User').exists():
            return reverse_lazy('participant_dashboard')  # Participant Dashboard
        else:
            return reverse_lazy('error')  # Error page for undefined roles
        
# Dashboard views for each user group
def event_organizer_dashboard(request):
    return render(request, 'dashboard/event_organizer_dashboard.html', {
        'title': 'Event Organizer Dashboard'
    })


def venue_manager_dashboard(request):
    return render(request, 'dashboard/venue_manager_dashboard.html', {
        'title': 'Venue Manager Dashboard'
    })


def participant_dashboard(request):
    events = Event.objects.all()
    return render(request, 'dashboard/participant_dashboard.html', {
        'title': 'Participant Dashboard' ,'events': events
    })


# Error Page View
def error_page(request):
    return render(request, 'error.html', {
        'message': 'You do not have the correct permissions to access this page.'
    })

def register_for_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    # Check if the user is already registered
    if EventRegistration.objects.filter(user=request.user, event=event).exists():
        messages.warning(request, "You are already registered for this event!")
        return redirect('user_dashboard')  # Redirect to dashboard

    # Register the user for the event
    EventRegistration.objects.create(user=request.user, event=event)
    messages.success(request, f"You have successfully registered for {event.name}!")
    
    return redirect('user_dashboard')  # Redirect to dashboard

def register_participant(request, event_id):
    event = Event.objects.get(id=event_id)
    registration_fee = 500  # Example fee
    participant = RegisteredParticipant(user=request.user, event=event, registration_fee=registration_fee)
    participant.save()
    messages.success(request, "You have successfully registered for the event. All the best!")
    return redirect('participant_dashboard')

def buy_ticket(request, event_id):
    event = Event.objects.get(id=event_id)
    ticket_price = 100  # Example ticket price
    viewer = EventViewer(user=request.user, event=event, ticket_price=ticket_price)
    viewer.save()
    messages.success(request, "Your ticket has been successfully booked.")
    return redirect('participant_dashboard')