from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('dashboard/event-organizer/', views.event_organizer_dashboard, name='event_organizer_dashboard'),
    path('dashboard/venue-manager/', views.venue_manager_dashboard, name='venue_manager_dashboard'),
    path('dashboard/participant/', views.participant_dashboard, name='participant_dashboard'),
    path('error/', views.error_page, name='error'),
    path('register/<int:event_id>/', views.register_for_event, name='register_for_event'),
    path('register/participant/<int:event_id>/', views.register_participant, name='register_participant'),
    path('buy/ticket/<int:event_id>/', views.buy_ticket, name='buy_ticket'),
    path('events/pay/<str:user_role>/<int:event_id>/', views.payment_page, name='payment_page'),
    path('payment/<str:user_role>/<int:event_id>/', views.payment_page, name='payment_page'),
    path('events/process_payment/<str:user_role>/<int:event_id>/', views.process_payment, name='process_payment'),
    # Dashboard view
    path('dashboard/', views.dashboard, name='dashboard'),
    path('events/create_event/', views.create_event, name='create_event'),
    path('events/update_event/<int:event_id>/', views.update_event, name='update_event'),
    path('events/delete_event/<int:event_id>/', views.delete_event, name='delete_event'),
    # path('events/view/others/', views.view_other_events, name='view_other_events'),
    path('', views.homepage, name='homepage'),
    path('dashboard/', views.organizer_dashboard, name='organizer_dashboard'),
    path('create_event/', views.create_event, name='create_event'),
    path('upcoming_events/', views.upcoming_events, name='upcoming_events'),
    path('participants_list/', views.participants_list, name='participants_list'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('homepage/', LogoutView.as_view(next_page='homepage'), name='logout'),
]

