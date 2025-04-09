from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

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
    path('history/', views.history_view, name='history'),  # ✅ Added History URL
    path('favorites/', views.favorite_view, name='favorite'),  # ✅ Added Favorites URL
    path('favorites/add/<int:history_id>/', views.add_favorite, name='add_favorite'),  # ✅ Add to Favorites
    path('favorites/remove/<int:favorite_id>/', views.remove_favorite, name='remove_favorite'),  # ✅ Remove from Favorites
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('reset-password/', views.reset_password_view, name='reset_password'),
    path('view_animation/<str:video_filename>/', views.load_animation_from_history, name='view_animation'),
    path('', views.home_view, name='home'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
