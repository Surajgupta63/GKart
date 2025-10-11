from django.urls import path
from . import views

urlpatterns = [
    # Razorpay order creation (AJAX called from frontend)
    path('create_razorpay_order/', views.create_razorpay_order, name='create_razorpay_order'),
    
    path('place_order/', views.place_order, name='place_order'),
    path('payments/', views.payments, name='payments'),
    path('order_complete/', views.order_complete, name='order_complete'),
]
