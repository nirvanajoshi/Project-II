from django.conf import settings
from django.db import models

# Event model stores all event details for the application.
class Event(models.Model):
    CATEGORY_SEMINAR = 'seminar'
    CATEGORY_WORKSHOP = 'workshop'
    CATEGORY_CONCERT = 'concert'
    CATEGORY_SPORTS = 'sports'
    CATEGORY_CULTURAL = 'cultural'

    CATEGORY_CHOICES = [
        (CATEGORY_SEMINAR, 'Seminar'),
        (CATEGORY_WORKSHOP, 'Workshop'),
        (CATEGORY_CONCERT, 'Concert'),
        (CATEGORY_SPORTS, 'Sports'),
        (CATEGORY_CULTURAL, 'Cultural Program'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default=CATEGORY_SEMINAR)
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=200)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='created_events'
    )
    approved = models.BooleanField(default=False)
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='Registration',
        related_name='registered_events',
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    venue = models.ForeignKey(
        'Venue',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='events'
    )
    max_participants = models.PositiveIntegerField(null=True, blank=True, help_text="Leave blank for unlimited participants")

    def __str__(self):
        # Display the event title in the admin and admin lists.
        return self.title

    def is_registered(self, user):
        # Return True if the given user is already registered for this event.
        return self.participants.filter(pk=user.pk).exists()
    
    def is_full(self):
        # Return True when the event has reached the maximum number of participants.
        if self.max_participants is None:
            return False
        return self.participants.count() >= self.max_participants
    
    def get_available_spots(self):
        # Calculate how many spots remain for the event.
        if self.max_participants is None:
            return None
        return self.max_participants - self.participants.count()

    def tickets_sold(self):
        # Count all confirmed booked tickets for this event.
        return Booking.objects.filter(ticket__event=self, status=Booking.STATUS_BOOKED).aggregate(models.Sum('quantity'))['quantity__sum'] or 0


# Registration model links a user to an event.
class Registration(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    registered_at = models.DateTimeField(auto_now_add=True)
    full_name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)

    class Meta:
        unique_together = ('user', 'event')

    def __str__(self):
        # Show a readable description for registration objects.
        return f"{self.user.username} registered for {self.event.title}"


# Venue holds information about event locations.
class Venue(models.Model):
    name = models.CharField(max_length=200)
    capacity = models.PositiveIntegerField()
    location = models.CharField(max_length=300)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# Ticket defines a ticket option for an event.
class Ticket(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='tickets')
    name = models.CharField(max_length=100, default='General')
    is_paid = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total_quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.name} - {self.event.title}"


# Booking stores a user's ticket order for an event.
class Booking(models.Model):
    STATUS_BOOKED = 'booked'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_BOOKED, 'Booked'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    booked_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_BOOKED)

    class Meta:
        unique_together = ('user', 'ticket')

    def __str__(self):
        return f"{self.user.username} booked {self.quantity} x {self.ticket.name} for {self.ticket.event.title}"


# Attendance records whether a user attended the event.
class Attendance(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    attended = models.BooleanField(default=False)
    marked_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'event')

    def __str__(self):
        return f"{self.user.username} attendance for {self.event.title}: {self.attended}"


# Notification stores messages for users about events.
class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification to {self.user.username}: {self.message[:40]}"
