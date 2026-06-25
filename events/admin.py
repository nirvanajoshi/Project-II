from django.contrib import admin
from .models import Event, Registration, Venue, Ticket, Booking, Attendance, Notification


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'approved', 'date', 'time', 'location')
    list_filter = ('approved', 'category', 'date')
    search_fields = ('title', 'description', 'location', 'created_by__username')


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'full_name', 'phone', 'registered_at')
    list_filter = ('event',)
    search_fields = ('user__username', 'full_name', 'phone', 'email')


admin.site.register(Venue)
admin.site.register(Ticket)
admin.site.register(Booking)
admin.site.register(Attendance)
admin.site.register(Notification)
