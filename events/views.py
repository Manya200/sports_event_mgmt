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
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Event, Organizer, Venue
from .forms import EventForm, EventUpdateForm ,VenueForm
from django.urls import reverse
from django.utils import timezone

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

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.models import Group
from .forms import CustomUserCreationForm

def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # The password is hashed automatically
            role = form.cleaned_data.get("role")  # This is one of: 'admin', 'event_organizer', 'user', 'venue_manager'
            
            # Map the selected role to the corresponding group (make sure the group names match exactly)
            if role == "admin":
                group = Group.objects.get(name="Admin")
            elif role == "event_organizer":
                group = Group.objects.get(name="Event Organizer")
            elif role == "user":
                group = Group.objects.get(name="User")
            elif role == "venue_manager":
                group = Group.objects.get(name="Venue Manager")
            
            user.groups.add(group)  # Automatically add the user to the chosen group
            login(request, user)    # Optionally, auto-login the user after registration
            messages.success(request, "Registration successful. You can now log in.")
            return redirect("login")  # Redirect to login (or another page) after successful registration
        else:
            messages.error(request, "Error in registration. Please check your details.")
    else:
        form = CustomUserCreationForm()

    return render(request, "registration/register_new_user.html", {"form": form})



def get_all_events_for_organizer(organizer):
    # Ensure you're using the User instance (not just a string)
    return Event.objects.filter(organizer=organizer)  # 'organizer' should be a User instance

# Dashboard views for each user group
def event_organizer_dashboard(request):
    events = Event.objects.all()
    print(events)
    return render(request, 'dashboard/event_organizer_dashboard.html', {
        'title': 'Event Organizer Dashboard','events' : events
    })

def venue_manager_dashboard(request):
    # Fetch all events (for Venue Manager to view)
    events = Event.objects.all()
    venues = Venue.objects.all()

    # Handle form submission for adding new venue
    if request.method == "POST":
        form = VenueForm(request.POST)
        if form.is_valid():
            form.save()  # Save the new venue to the database
            return redirect('venue_manager_dashboard')  # Redirect back to the dashboard after saving the venue
    else:
        form = VenueForm()

    return render(request, 'dashboard/venue_manager_dashboard.html', {
        'title': 'Venue Manager Dashboard',
        'events': events,
        'form': form,
        'venues': venues
    })

# Fetch all events (helper function)
def get_all_events():
    return Event.objects.all()


def participant_dashboard(request):
    events = Event.objects.all()
    # events = get_all_events()  # Reuse the helper functions
    print(events)
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


@login_required
def update_event(request, event_id):
    organizer = get_object_or_404(Organizer, user=request.user)
    event = get_object_or_404(Event, id=event_id, organizer=organizer)
    if request.method == 'POST':
        form = EventUpdateForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = EventUpdateForm(instance=event)
    return render(request, 'events/update_event.html', {'form': form, 'event': event})

@login_required
def delete_event(request, event_id):
    organizer = get_object_or_404(Organizer, user=request.user)
    event = get_object_or_404(Event, id=event_id, organizer=organizer)
    if request.method == 'POST':
        event.delete()
        return redirect('dashboard')
    return render(request, 'events/delete_event.html', {'event': event})

@login_required
def view_other_events(request):
    other_events = Event.objects.exclude(organizer__user=request.user).filter(is_active=True)
    return render(request, 'events/view_other_events.html', {'events': other_events})


# Organizer Dashboard
@login_required
def organizer_dashboard(request):
    events = get_all_events_for_organizer(request.user)  # Fetch all events
    print(get_all_events_for_organizer(request.user))
    return render(request, 'dashboard/event_organizer_dashboard.html', {
        'title': 'Organizer Dashboard',
        'events': events
    })

# Organizer's Specific Dashboard # Dashboard - Show only the organizer's events
@login_required
def dashboard(request):
    # Fetch all events and filter for the current organizer
    events = Event.objects.all()  # Get all events
    organizer_events = events.filter(organizer__user=request.user)  # Filter events for the logged-in organizer
    venues = Venue.objects.all()

    return render(request, 'dashboard/dashboard.html', {
        'title': 'Your Dashboard',
        'organizer_events': organizer_events,  # Pass the filtered events
        'venues': venues,
    })



@login_required
def create_event(request):
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        registration_fee = request.POST.get("registration_fee")
        ticket_price = request.POST.get("ticket_price")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        venue_id = request.POST.get("venue")

        # Validation
        if not name or not description or not start_date or not end_date or not venue_id:
            return render(request, 'create_event.html', {
                'error': "All fields are required.",
            })

        if start_date >= end_date:
            return render(request, 'create_event.html', {
                'error': "Start date must be before end date.",
            })

        # Fetch or create the organizer
        organizer, created = Organizer.objects.get_or_create(user=request.user)

        # Ensure the venue exists
        venue = get_object_or_404(Venue, id=venue_id)

        # Create and save the event
        Event.objects.create(
            name=name,
            description=description,
            registration_fee=registration_fee,
            ticket_price=ticket_price,
            start_date=start_date,
            end_date=end_date,
            venue=venue,
            organizer=organizer,
        )

        return redirect(reverse("dashboard"))

    venues = Venue.objects.all()  # Fetch venues for event creation form
    return render(request, 'create_event.html', {
        'venues': venues,
    })

# Upcoming Events
@login_required
def upcoming_events(request):
    try:
        # Get the organizer object for the logged-in user
        organizer = request.user
        
        # Fetch all upcoming events
        events = Event.objects.filter(organizer=request.user, start_date__gte=timezone.now())
        
        context = {
            'events': events,
        }
    except Organizer.DoesNotExist:
        # Handle case where the user is not an organizer
        return render(request, 'error.html', {'message': 'You are not authorized to access this page.'})
    
    return render(request, 'upcoming_events.html', context)


# Participant List for Organizer Events
@login_required
def participants_list(request):
    try:
        # Get the organizer object for the logged-in user
        organizer = request.user.organizer
        
        # Fetch participants for the organizer's events
        events = Event.objects.filter(organizer=organizer)
        participants = EventRegistration.objects.filter(event__in=events)
        
        context = {
            'participants': participants,
        }
    except Organizer.DoesNotExist:
        # Handle case where the user is not an organizer
        return render(request, 'error.html', {'message': 'You are not authorized to access this page.'})
    
    return render(request, 'participants_list.html', context)



# View participants for a specific event (new function)
@login_required
def participants(request, event_id):
    organizer = get_object_or_404(Organizer, user=request.user)
    event = get_object_or_404(Event, id=event_id, organizer=organizer)
    participants = RegisteredParticipant.objects.filter(event=event)
    return render(request, 'participants.html', {'event': event, 'participants': participants})

# Event Details View (new function)
@login_required
def event_details(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'event_details.html', {'event': event})

# Delete Event Confirmation (updated function)
@login_required
def delete_event(request, event_id):
    organizer = get_object_or_404(Organizer, user=request.user)
    event = get_object_or_404(Event, id=event_id, organizer=organizer)
    if request.method == 'POST':
        event.delete()
        messages.success(request, "Event deleted successfully.")
        return redirect('dashboard')
    return render(request, 'events/delete_event.html', {'event': event})

# Search and Filter Events (new function)
@login_required
def search_events(request):
    query = request.GET.get('query', '')
    events = Event.objects.filter(name__icontains=query, start_date__gte=timezone.now())
    return render(request, 'search_events.html', {'events': events, 'query': query})

# Edit Profile View (new function)
@login_required
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('profile')
    return render(request, 'edit_profile.html', {'user': user})


