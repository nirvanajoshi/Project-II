from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('events/create/', views.create_event, name='create_event'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('events/<int:event_id>/edit/', views.update_event, name='update_event'),
    path('events/<int:event_id>/delete/', views.delete_event, name='delete_event'),
    path('events/<int:event_id>/register/', views.register_for_event, name='register_for_event'),
    path('events/<int:event_id>/cancel/', views.cancel_registration, name='cancel_registration'),
    path('events/<int:event_id>/participants/', views.event_participants, name='event_participants'),
]
