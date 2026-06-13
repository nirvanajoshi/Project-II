from django.db.models import Q
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
    context = {
        'events_count': Event.objects.count(),
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
    event = get_object_or_404(Event, pk=event_id)
    Registration.objects.get_or_create(user=request.user, event=event)
    return redirect('event_detail', event_id=event.id)


@login_required
def cancel_registration(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    Registration.objects.filter(user=request.user, event=event).delete()
    return redirect('event_detail', event_id=event.id)


@login_required
def event_participants(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    participants = event.participants.order_by('username')
    return render(request, 'events/event_participants.html', {'event': event, 'participants': participants})
