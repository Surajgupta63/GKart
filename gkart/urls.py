from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('store/', include('store.urls')),
    path('cart/', include('carts.urls')),
    path('accounts/', include('accounts.urls')),  ## my custom accounts urls
    path('orders/', include('orders.urls')),

    path('accounts/', include('allauth.urls')),  ## social auth urls
    path('health/', views.health, name='health'),  # for healtg checking
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
