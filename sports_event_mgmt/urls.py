from django.contrib import admin
from django.urls import path
# from events import views  # Import the view
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
# from .views import CustomLoginView
from events.views import CustomLoginView
from django.urls import path, include

urlpatterns = [
    path('', TemplateView.as_view(template_name='homepage.html'), name='home'),
    path('admin/', admin.site.urls),  # Admin login
    # path('user/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),  # User login
    path('user/login/', CustomLoginView.as_view(), name='login'),
    path('events/', include('events.urls')),
]
