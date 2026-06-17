from django.contrib import admin
from .models import Event, Registration

admin.site.register(Event)
admin.site.register(Registration)

from .models import Venue, Ticket, Booking, Attendance, Notification

admin.site.register(Venue)
admin.site.register(Ticket)
admin.site.register(Booking)
admin.site.register(Attendance)
admin.site.register(Notification)
