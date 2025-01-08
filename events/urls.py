from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/event-organizer/', views.event_organizer_dashboard, name='event_organizer_dashboard'),
    path('dashboard/venue-manager/', views.venue_manager_dashboard, name='venue_manager_dashboard'),
    path('dashboard/participant/', views.participant_dashboard, name='participant_dashboard'),
    path('error/', views.error_page, name='error'),
    path('register/<int:event_id>/', views.register_for_event, name='register_for_event'),
    path('register/participant/<int:event_id>/', views.register_participant, name='register_participant'),
    path('buy/ticket/<int:event_id>/', views.buy_ticket, name='buy_ticket'),

]

