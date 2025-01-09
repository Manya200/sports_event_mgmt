from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.http import HttpResponse, FileResponse
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from reportlab.pdfgen import canvas
import logging
import io
from .models import Event, EventRegistration, RegisteredParticipant, EventViewer

def homepage(request):
    return render(request, 'homepage.html')

# Custom Login View
class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def get_success_url(self):
        user = self.request.user
        # Redirect based on user group
        if user.groups.filter(name='Event Organizer').exists():
            return reverse_lazy('event_organizer_dashboard')
        elif user.groups.filter(name='Venue Manager').exists():
            return reverse_lazy('venue_manager_dashboard')
        elif user.groups.filter(name='User').exists():
            return reverse_lazy('participant_dashboard')
        else:
            return reverse_lazy('error')

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
        'title': 'Participant Dashboard', 'events': events
    })

# Error Page View
def error_page(request):
    return render(request, 'error.html', {
        'message': 'You do not have the correct permissions to access this page.'
    })

# Register for event
def register_for_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    # Check if the user is already registered
    if EventRegistration.objects.filter(user=request.user, event=event).exists():
        messages.warning(request, "You are already registered for this event!")
        return redirect('participant_dashboard')

    # Register the user for the event
    EventRegistration.objects.create(user=request.user, event=event)
    messages.success(request, f"You have successfully registered for {event.name}!")

    return redirect('participant_dashboard')

# Register participant
def register_participant(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    registration_fee = event.registration_fee  # Fetch registration fee from event model
    participant = RegisteredParticipant(user=request.user, event=event, registration_fee=registration_fee)
    participant.save()
    messages.success(request, "You have successfully registered for the event. All the best!")
    return redirect('participant_dashboard')

# Buy ticket
def buy_ticket(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    ticket_price = event.ticket_price  # Fetch ticket price from event model
    viewer = EventViewer(user=request.user, event=event, ticket_price=ticket_price)
    viewer.save()
    messages.success(request, "Your ticket has been successfully booked.")
    return redirect('participant_dashboard')

# Send email notification
def send_email_notification(user, user_role, event):
    subject = "Registration/Ticket Confirmation"
    if user_role == "Participant":
        message = f"Dear {user.username},\n\nYou have successfully registered for the event: {event.name}. All the best!"
    elif user_role == "Viewer":
        message = f"Dear {user.username},\n\nYour ticket for the event: {event.name} has been successfully booked. Enjoy the event!"

    recipient_list = [user.email]
    from_email = settings.EMAIL_HOST_USER

    try:
        send_mail(subject, message, from_email, recipient_list)
    except Exception as e:
        logging.error(f"Error sending email: {e}")

# Payment page
def payment_page(request, user_role, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'payment_page.html', {'event': event, 'user_role': user_role})

# Generate receipt
def generate_receipt(user, user_role, event, amount_paid):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)

    # Receipt Title
    c.setFont("Helvetica-Bold", 20)
    c.drawString(100, 800, "Payment Receipt")

    # User and Event Details
    c.setFont("Helvetica", 12)
    c.drawString(50, 750, f"Name: {user.username}")
    c.drawString(50, 730, f"Role: {user_role.title()}")
    c.drawString(50, 710, f"Event: {event.name}")
    c.drawString(50, 690, f"Date: {event.start_date.strftime('%Y-%m-%d %H:%M:%S')}")

    # Payment Information
    c.drawString(50, 670, f"Amount Paid: ₹{amount_paid}")
    c.drawString(50, 650, "Payment Status: Successful")

    # Footer
    c.drawString(50, 600, "Thank you for your payment!")
    c.drawString(50, 580, "Enjoy the event!")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# Process payment
def process_payment(request, user_role, event_id):
    if request.method == "POST":
        upi_id = request.POST.get('upi_id')
        event = get_object_or_404(Event, id=event_id)

        if user_role == "participant":
            amount_paid = event.registration_fee
            participant = RegisteredParticipant(user=request.user, event=event, registration_fee=amount_paid)
            participant.save()
            messages.success(request, "You have successfully registered for the event. All the best!")
        elif user_role == "viewer":
            amount_paid = event.ticket_price
            viewer = EventViewer(user=request.user, event=event, ticket_price=amount_paid)
            viewer.save()
            messages.success(request, "Your ticket has been successfully booked.")

        # Generate Receipt
        buffer = generate_receipt(request.user, user_role, event, amount_paid)
        return FileResponse(buffer, as_attachment=True, filename="payment_receipt.pdf")

    return redirect('error')
