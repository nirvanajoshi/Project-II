from django.urls import path
from . import views

urlpatterns = [
    # Home page with event list and search filters.
    path('', views.home, name='home'),
    # Create a new event page.
    path('events/create/', views.create_event, name='create_event'),
    # Event detail page.
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    # Update event page for the event owner.
    path('events/<int:event_id>/edit/', views.update_event, name='update_event'),
    # Confirm delete event page.
    path('events/<int:event_id>/delete/', views.delete_event, name='delete_event'),
    # Register or unregister from an event.
    path('events/<int:event_id>/register/', views.register_for_event, name='register_for_event'),
    path('events/<int:event_id>/cancel/', views.cancel_registration, name='cancel_registration'),
    # View event participants page.
    path('events/<int:event_id>/participants/', views.event_participants, name='event_participants'),
    # Book tickets for an event.
    path('events/<int:event_id>/book/', views.book_ticket, name='book_ticket'),
    # Cancel a specific ticket booking.
    path('booking/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),

    # Venue management pages.
    path('venues/', views.venue_list, name='venue_list'),
    path('venues/create/', views.venue_create, name='venue_create'),
    path('venues/<int:venue_id>/edit/', views.venue_update, name='venue_update'),
    path('venues/<int:venue_id>/delete/', views.venue_delete, name='venue_delete'),

    # Mark a user's attendance for an event.
    path('events/<int:event_id>/attendance/<int:user_id>/mark/', views.mark_attendance, name='mark_attendance'),
    # Notifications page for the logged-in user.
    path('notifications/', views.notifications, name='notifications'),
]
