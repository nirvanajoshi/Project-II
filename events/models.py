from django.conf import settings
from django.db import models

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
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='Registration',
        related_name='registered_events',
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def is_registered(self, user):
        return self.participants.filter(pk=user.pk).exists()


class Registration(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'event')

    def __str__(self):
        return f"{self.user.username} registered for {self.event.title}"
