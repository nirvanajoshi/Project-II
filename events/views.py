from django.db.models import Q, Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from .models import Event, Registration
from .forms import EventForm


def home(request):
    events = Event.objects.order_by('date', 'time')
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()

    if query:
        events = events.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(location__icontains=query)
        )

    if category:
        events = events.filter(category=category)

    context = {
        'events': events,
        'query': query,
        'selected_category': category,
        'categories': Event.CATEGORY_CHOICES,
    }
    return render(request, 'home.html', context)


@login_required
def dashboard(request):
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
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            form.save_m2m()
            return redirect('event_detail', event_id=event.id)
    else:
        form = EventForm()
    return render(request, 'events/event_form.html', {'form': form, 'action': 'Create Event'})


def event_detail(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    is_registered = request.user.is_authenticated and event.is_registered(request.user)
    return render(request, 'events/event_detail.html', {'event': event, 'is_registered': is_registered})


@login_required
def book_ticket(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    tickets = event.tickets.all()
    if request.method == 'POST':
        from .forms import BookingForm
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            # simple availability check
            if booking.quantity <= booking.ticket.total_quantity:
                booking.save()
            return redirect('event_detail', event_id=event.id)
    else:
        from .forms import BookingForm
        form = BookingForm()
    return render(request, 'events/event_form.html', {'form': form, 'action': 'Book Ticket', 'event': event, 'tickets': tickets})


@login_required
def cancel_booking(request, booking_id):
    from .models import Booking
    booking = get_object_or_404(Booking, pk=booking_id)
    if booking.user != request.user:
        return redirect('event_detail', event_id=booking.ticket.event.id)
    booking.status = Booking.STATUS_CANCELLED
    booking.save()
    return redirect('event_detail', event_id=booking.ticket.event.id)


@login_required
def venue_list(request):
    from .models import Venue
    venues = Venue.objects.order_by('name')
    return render(request, 'events/venue_list.html', {'venues': venues})


@login_required
def venue_create(request):
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
    from .models import Venue
    venue = get_object_or_404(Venue, pk=venue_id)
    if request.method == 'POST':
        venue.delete()
        return redirect('venue_list')
    return render(request, 'events/event_confirm_delete.html', {'event': venue})


@login_required
def mark_attendance(request, event_id, user_id):
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
    from .models import Notification
    notes = Notification.objects.filter(user=request.user).order_by('-sent_at')
    return render(request, 'events/notifications.html', {'notifications': notes})


@login_required
def update_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if event.created_by and event.created_by != request.user:
        return redirect('event_detail', event_id=event.id)

    form = EventForm(request.POST or None, instance=event)
    if form.is_valid():
        form.save()
        return redirect('event_detail', event_id=event.id)
    return render(request, 'events/event_form.html', {'form': form, 'action': 'Update Event', 'event': event})


@login_required
def delete_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if event.created_by and event.created_by != request.user:
        return redirect('event_detail', event_id=event.id)

    if request.method == 'POST':
        event.delete()
        return redirect('home')
    return render(request, 'events/event_confirm_delete.html', {'event': event})


@login_required
def register_for_event(request, event_id):
    from .forms import RegistrationForm
    from .models import Notification

    event = get_object_or_404(Event, pk=event_id)

    # show form to collect participant details
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            reg, created = Registration.objects.get_or_create(user=request.user, event=event)
            reg.full_name = form.cleaned_data.get('full_name')
            reg.email = form.cleaned_data.get('email')
            reg.phone = form.cleaned_data.get('phone')
            reg.address = form.cleaned_data.get('address')
            reg.save()

            # notify organizer
            if event.created_by:
                Notification.objects.create(
                    user=event.created_by,
                    event=event,
                    message=f"{request.user.username} registered for {event.title}."
                )

            return redirect('event_detail', event_id=event.id)
    else:
        form = RegistrationForm()

    return render(request, 'events/register_form.html', {'form': form, 'event': event})


@login_required
def cancel_registration(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    Registration.objects.filter(user=request.user, event=event).delete()
    return redirect('event_detail', event_id=event.id)


@login_required
def event_participants(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    from .models import Registration
    # only show full list to organizer or staff; other users see their own registration
    if request.user == event.created_by or request.user.is_staff:
        registrations = Registration.objects.filter(event=event).order_by('registered_at')
    else:
        registrations = Registration.objects.filter(event=event, user=request.user)
    return render(request, 'events/event_participants.html', {'event': event, 'registrations': registrations})
