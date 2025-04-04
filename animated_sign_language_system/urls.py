from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

# Custom error handlers
handler404 = 'animated_sign_language_system.views.error_404_view'
handler500 = 'animated_sign_language_system.views.error_500_view'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('animation/', views.animation_view, name='animation'),
    path('', views.home_view, name='home'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
