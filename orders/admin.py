from django.contrib import admin
from .models import Payment, Order, OrderProduct

class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('payment', 'user', 'product', 'quantity', 'product_price', 'ordered')
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'full_name', 'phone', 'email', 'city', 'order_total', 'tax', 'status', 'is_ordered', 'created_at']
    list_filter = ['status', 'is_ordered']
    search_fields = ['order_number', 'first_name', 'last_name', 'phone', 'email']
    list_per_page = 10
    inlines = [OrderProductInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(orderproduct__product__owner=request.user).distinct()

    # Seller can only view orders (not edit/delete)
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'payment_id', 'payment_method', 'amount_paid', 'status', 'created_at')
    list_filter = ('status', 'payment_method')
    search_fields = ('user', 'status')
    list_display_links = ('user', 'payment_id')
    list_per_page = 10

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser

class OrderProductAdmin(admin.ModelAdmin):
    list_display = ('product', 'seller', 'user', 'quantity', 'order', 'product_price', 'ordered')
    list_filter = ( 'seller', 'ordered')
    search_fields = ('product', )
    list_display_links = ('product', 'user')
    list_per_page = 10

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(product__owner=request.user)

    # Seller cannot delete or edit order products
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser
    

# Register your models here.
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct, OrderProductAdmin)