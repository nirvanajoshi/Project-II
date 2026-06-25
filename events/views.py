# views.py handles the request/response logic for the event app.
# Each function here is a view that returns an HTML page or performs an action.
from django.db.models import Q, Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages

from .models import Event, Registration
from .forms import EventForm


def home(request):
    # Render the main event listing page with search and filter support.
    now = timezone.now().date()
    events = Event.objects.order_by('date', 'time')

    if request.user.is_staff:
        # Admin can see all host events, but upcoming schedule should still show only approved events.
        host_events = events.filter(created_by=request.user).order_by('date', 'time') if request.user.is_authenticated else None
        upcoming_events = events.filter(approved=True, canceled=False, date__gte=now).order_by('date', 'time')
    elif request.user.is_authenticated:
        # Logged-in users can see approved upcoming events and their own host events.
        host_events = events.filter(created_by=request.user).order_by('date', 'time')
        upcoming_events = events.filter(approved=True, canceled=False, date__gte=now).order_by('date', 'time')
    else:
        # Anonymous users only see approved upcoming events.
        host_events = None
        upcoming_events = events.filter(approved=True, canceled=False, date__gte=now).order_by('date', 'time')

    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()

    if query:
        # If the user searched for a keyword, filter the events by title, description, or location.
        upcoming_events = upcoming_events.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(location__icontains=query)
        )
        if host_events is not None:
            host_events = host_events.filter(
                Q(title__icontains=query)
                | Q(description__icontains=query)
                | Q(location__icontains=query)
            )

    if category:
        # If the user selected a category, filter events by that category.
        upcoming_events = upcoming_events.filter(category=category)
        if host_events is not None:
            host_events = host_events.filter(category=category)

    context = {
        'events': upcoming_events,
        'host_events': host_events,
        'query': query,
        'selected_category': category,
        'categories': Event.CATEGORY_CHOICES,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Return only the event list HTML when this is an AJAX request.
        return render(request, 'events/_event_list.html', context)

    # Render the full home page otherwise.
    return render(request, 'home.html', context)


@login_required
def dashboard(request):
    # Show the organizer dashboard for logged-in users only.
    from .models import Booking, Attendance
    from django.utils import timezone

    events_count = Event.objects.count()
    participants_count = Registration.objects.count()
    upcoming_events = Event.objects.filter(date__gte=timezone.now().date()).order_by('date')[:5]
    tickets_sold = Booking.objects.filter(status=Booking.STATUS_BOOKED).aggregate(Sum('quantity'))['quantity__sum'] or 0

    context = {
        'events_count': events_count,
        'participants_count': participants_count,
        'upcoming_events': upcoming_events,
        'tickets_sold': tickets_sold,
    }
    return render(request, 'dashboard.html', context)


def register(request):
    # Display a signup form and create a new user when the form is submitted.
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def create_event(request):
    # Allow authenticated users to create new events.
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.approved = False
            event.save()
            form.save_m2m()
            messages.success(request, 'Event created and is pending admin approval.')
            return redirect('event_detail', event_id=event.id)
    else:
        form = EventForm()
    return render(request, 'events/event_form.html', {'form': form, 'action': 'Create Event', 'event': None})


def event_detail(request, event_id):
    # Show detail page for a single event.
    event = get_object_or_404(Event, pk=event_id)
    if event.canceled and request.user != event.created_by and not request.user.is_staff:
        messages.error(request, 'This event has been canceled and is not available.')
        return redirect('home')
    if not event.approved and request.user != event.created_by and not request.user.is_staff:
        messages.error(request, 'This event is pending admin approval and is not visible yet.')
        return redirect('home')

    is_registered = request.user.is_authenticated and event.is_registered(request.user)
    participant_count = event.participants.count()
    is_full = event.is_full()
    available_spots = event.get_available_spots()
    return render(request, 'events/event_detail.html', {
        'event': event,
        'is_registered': is_registered,
        'participant_count': participant_count,
        'is_full': is_full,
        'available_spots': available_spots
    })


@login_required
def book_ticket(request, event_id):
    # Allow a logged-in user to book a ticket for a specific event.
    event = get_object_or_404(Event, pk=event_id)
    tickets = event.tickets.all()
    if request.method == 'POST':
        from .forms import BookingForm
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            # Simple check to avoid booking more tickets than exist.
            if booking.quantity <= booking.ticket.total_quantity:
                booking.save()
            return redirect('event_detail', event_id=event.id)
    else:
        from .forms import BookingForm
        form = BookingForm()
    return render(request, 'events/event_form.html', {'form': form, 'action': 'Book Ticket', 'event': event, 'tickets': tickets})


@login_required
def cancel_booking(request, booking_id):
    # Let the booking owner cancel a ticket booking.
    from .models import Booking
    booking = get_object_or_404(Booking, pk=booking_id)
    if booking.user != request.user:
        return redirect('event_detail', event_id=booking.ticket.event.id)
    booking.status = Booking.STATUS_CANCELLED
    booking.save()
    return redirect('event_detail', event_id=booking.ticket.event.id)


@login_required
def venue_list(request):
    # Show the list of venues for the admin or organizer.
    from .models import Venue
    venues = Venue.objects.order_by('name')
    return render(request, 'events/venue_list.html', {'venues': venues})


@login_required
def venue_create(request):
    # Create a new venue record.
    from .forms import VenueForm
    if request.method == 'POST':
        form = VenueForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('venue_list')
    else:
        form = VenueForm()
    return render(request, 'events/event_form.html', {'form': form, 'action': 'Create Venue'})


@login_required
def venue_update(request, venue_id):
    # Edit an existing venue's data.
    from .models import Venue
    from .forms import VenueForm
    venue = get_object_or_404(Venue, pk=venue_id)
    form = VenueForm(request.POST or None, instance=venue)
    if form.is_valid():
        form.save()
        return redirect('venue_list')
    return render(request, 'events/event_form.html', {'form': form, 'action': 'Update Venue'})


@login_required
def venue_delete(request, venue_id):
    # Delete a venue if the delete form is submitted.
    from .models import Venue
    venue = get_object_or_404(Venue, pk=venue_id)
    if request.method == 'POST':
        venue.delete()
        return redirect('venue_list')
    return render(request, 'events/event_confirm_delete.html', {'event': venue})


@login_required
def mark_attendance(request, event_id, user_id):
    # Mark a user as having attended a specific event.
    from .models import Attendance
    from django.contrib.auth import get_user_model
    User = get_user_model()
    event = get_object_or_404(Event, pk=event_id)
    user = get_object_or_404(User, pk=user_id)
    attendance, created = Attendance.objects.get_or_create(user=user, event=event)
    attendance.attended = True
    attendance.save()
    return redirect('event_participants', event_id=event.id)


@login_required
def notifications(request):
    # Show notifications created for the current logged-in user.
    from .models import Notification
    notes = Notification.objects.filter(user=request.user).order_by('-sent_at')
    return render(request, 'events/notifications.html', {'notifications': notes})


@login_required
def update_event(request, event_id):
    # Allow the event creator to edit event details.
    event = get_object_or_404(Event, pk=event_id)
    if event.created_by and event.created_by != request.user:
        return redirect('event_detail', event_id=event.id)

    if event.approved and not request.user.is_staff:
        messages.error(request, 'This event has already been approved and cannot be edited here. Please contact an admin for changes.')
        return redirect('event_detail', event_id=event.id)

    form = EventForm(request.POST or None, instance=event)
    if form.is_valid():
        event = form.save(commit=False)
        if not request.user.is_staff:
            event.approved = False
        event.save()
        form.save_m2m()
        messages.success(request, 'Event updated. It will remain pending approval until an admin approves it.' if not request.user.is_staff else 'Event updated.')
        return redirect('event_detail', event_id=event.id)
    return render(request, 'events/event_form.html', {'form': form, 'action': 'Update Event', 'event': event})


@login_required
def delete_event(request, event_id):
    # Delete an event only when the creator confirms on the delete page.
    event = get_object_or_404(Event, pk=event_id)
    if event.created_by and event.created_by != request.user:
        return redirect('event_detail', event_id=event.id)

    if request.method == 'POST':
        event.delete()
        return redirect('home')
    return render(request, 'events/event_confirm_delete.html', {'event': event})


@login_required
def register_for_event(request, event_id):
    # Show registration form and save registration details.
    from .forms import RegistrationForm
    from .models import Notification
    from django.contrib import messages

    event = get_object_or_404(Event, pk=event_id)

    if event.canceled:
        messages.error(request, 'This event has been canceled and registration is closed.')
        return redirect('event_detail', event_id=event.id)

    if event.is_full() and not event.is_registered(request.user):
        # Prevent registration when event has no available seats.
        messages.error(request, f'Sorry! {event.title} has reached the maximum number of participants.')
        return redirect('event_detail', event_id=event.id)

    if not event.approved:
        messages.error(request, 'This event is pending admin approval. Registration is not available yet.')
        return redirect('event_detail', event_id=event.id)

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            if event.is_full() and not event.is_registered(request.user):
                messages.error(request, f'Sorry! {event.title} has reached the maximum number of participants.')
                return redirect('event_detail', event_id=event.id)
            
            reg, created = Registration.objects.get_or_create(user=request.user, event=event)
            reg.full_name = form.cleaned_data.get('full_name')
            reg.email = form.cleaned_data.get('email')
            reg.phone = form.cleaned_data.get('phone')
            reg.address = form.cleaned_data.get('address')
            reg.save()

            if event.created_by:
                Notification.objects.create(
                    user=event.created_by,
                    event=event,
                    message=f"{request.user.username} registered for {event.title}."
                )

            messages.success(request, f'You have successfully registered for {event.title}!')
            return redirect('event_detail', event_id=event.id)
    else:
        form = RegistrationForm()

    return render(request, 'events/register_form.html', {'form': form, 'event': event})


@login_required
def cancel_registration(request, event_id):
    # Remove current user registration for the event if they cancel.
    event = get_object_or_404(Event, pk=event_id)
    Registration.objects.filter(user=request.user, event=event).delete()
    return redirect('event_detail', event_id=event.id)


@login_required
def event_participants(request, event_id):
    # Show the participant list only to the event organizer or staff.
    event = get_object_or_404(Event, pk=event_id)
    from .models import Registration
    if request.user != event.created_by and not request.user.is_staff:
        return redirect('event_detail', event_id=event.id)
    
    registrations = Registration.objects.filter(event=event).order_by('registered_at')
    return render(request, 'events/event_participants.html', {'event': event, 'registrations': registrations})
