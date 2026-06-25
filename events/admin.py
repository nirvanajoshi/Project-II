from django.contrib import admin
from .models import Event, Registration, Venue, Ticket, Booking, Attendance, Notification


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'approved', 'canceled', 'date', 'time', 'location')
    list_editable = ('approved', 'canceled')
    list_filter = ('approved', 'canceled', 'category', 'date')
    search_fields = ('title', 'description', 'location', 'created_by__username')
    actions = ('approve_events', 'mark_pending', 'cancel_events', 'uncancel_events')

    @admin.action(description='Approve selected events')
    def approve_events(self, request, queryset):
        updated = queryset.update(approved=True, canceled=False)
        self.message_user(request, f'{updated} event(s) marked as approved.')

    @admin.action(description='Mark selected events as pending approval')
    def mark_pending(self, request, queryset):
        updated = queryset.update(approved=False, canceled=False)
        self.message_user(request, f'{updated} event(s) marked as pending approval.')

    @admin.action(description='Mark selected events as canceled')
    def cancel_events(self, request, queryset):
        updated = queryset.update(canceled=True)
        self.message_user(request, f'{updated} event(s) marked as canceled.')

    @admin.action(description='Uncancel selected events')
    def uncancel_events(self, request, queryset):
        updated = queryset.update(canceled=False)
        self.message_user(request, f'{updated} event(s) marked as uncanceled.')


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
