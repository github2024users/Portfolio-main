from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from port_folio import views

urlpatterns = [
path('admin/', admin.site.urls),
path('', views.homepage, name="homepage"),
path('contactus', views.Contactus, name="contactus"),
path('register', views.register, name="register"),
path('login', views.login, name="login"),
path('dashboard', views.dashboard, name="dashboard"),
path('profiledetails/', include('profiledetails.urls')),
]

# Serve uploaded media files (resume, images, etc.)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
