from django.contrib import admin
from .models import Product, Variation, ReviewRating, ProductGallery
import admin_thumbnails

@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ('product_name',)}
    list_display = ('product_name', 'price', 'stock', 'category', 'updated_at', 'is_available', 'owner')
    exclude = ('owner', )
    list_per_page = 10
    inlines = [ProductGalleryInline]

    # Show only seller’s own products (superuser sees all)
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Only show products owned by the logged-in user
        return qs.filter(owner=request.user)

    # Assign owner automatically when creating
    def save_model(self, request, obj, form, change):
        if not change:  # only assign owner on create
            obj.owner = request.user
        super().save_model(request, obj, form, change)

    # Allow delete only for own products or superuser
    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:  # allow bulk delete only if qs filtered by get_queryset
            return True
        return obj.owner == request.user

    # Allow add only to superuser or staff (seller)
    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.is_staff

    # Allow edit only for own products or superuser
    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return True  # allow access to changelist, filtering will happen in get_queryset
        return obj.owner == request.user

    

class VariationAdmin(admin.ModelAdmin):
    list_display  = ('product', 'variation_category', 'variation_value', 'is_active')
    list_editable = ('is_active',)
    list_filter   = ('product', 'variation_category', 'variation_value')

     # Show only variations of products owned by this user
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(product__owner=request.user)

    # Allow sellers to add variations only for their products
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "product" and not request.user.is_superuser:
            kwargs["queryset"] = Product.objects.filter(owner=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.is_staff

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj and obj.product.owner != request.user:
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj and obj.product.owner != request.user:
            return False
        return True

# Register your models here.
admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)
admin.site.register(ReviewRating)
admin.site.register(ProductGallery)