from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.timezone import now  # For date comparisons

# Organizer Model
class Organizer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organization_name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=15)

    def __str__(self):
        return self.organization_name


# Venue Model
class Venue(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return self.name


# Event Model
class Event(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)
    organizer = models.ForeignKey(Organizer, on_delete=models.CASCADE,related_name='events')
    registration_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def clean(self):
        if self.start_date >= self.end_date:
            raise ValidationError("End date must be after the start date.")

    @property
    def is_upcoming(self):
        """Check if the event is upcoming."""
        return self.start_date >= now()

    @property
    def total_participants(self):
        """Count total registered participants for this event."""
        return RegisteredParticipant.objects.filter(event=self).count()


# Event Registration Model
class EventRegistration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    registration_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} registered for {self.event.name}'


# Registered Participant Model
class RegisteredParticipant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    registration_fee = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='Pending')

    def __str__(self):
        return f'{self.user.username} for {self.event.name}'


# Event Viewer Model
class EventViewer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='Pending')

    def __str__(self):
        return f'{self.user.username} viewing {self.event.name}'
