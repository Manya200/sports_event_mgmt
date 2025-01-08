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
from django.core.mail import send_mail
from django.conf import settings

def homepage(request):
    return render(request, 'homepage.html')

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
# to send notification on email
def send_email_notification(user, role, event):
    subject = "Registration/Ticket Confirmation"
    if role == "Participant":
        message = f"Dear {user.username},\n\nYou have successfully registered for the event: {event.name}. All the best!"
    elif role == "Viewer":
        message = f"Dear {user.username},\n\nYour ticket for the event: {event.name} has been successfully booked. Enjoy the event!"
    
    recipient_list = [user.email]
    from_email = settings.EMAIL_HOST_USER
    
    send_mail(subject, message, from_email, recipient_list)


def payment_page(request, user_role, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'payment_page.html', {'event': event, 'user_role': user_role})

def process_payment(request, user_role, event_id):
    if request.method == "POST":
        upi_id = request.POST.get('upi_id')
        event = get_object_or_404(Event, id=event_id)

        if user_role == "participant":
            # Save participant registration
            participant = RegisteredParticipant(user=request.user, event=event, registration_fee=500)
            participant.save()
            messages.success(request, "You have successfully registered for the event. All the best!")
            send_email_notification(request.user, "Participant", event)
        elif user_role == "viewer":
            # Save viewer ticket
            viewer = EventViewer(user=request.user, event=event, ticket_price=100)
            viewer.save()
            messages.success(request, "Your ticket has been successfully booked.")
            send_email_notification(request.user, "Viewer", event)

        return redirect('participant_dashboard')
    else:
        return redirect('error')