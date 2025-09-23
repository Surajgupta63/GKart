from django.shortcuts import render
from store.models import Product, ReviewRating
from django.contrib.auth.decorators import login_required

def home(request):
    products = Product.objects.all().filter(is_available=True).order_by('created_at')

    reviews = None
    for product in products:
        reviews = ReviewRating.objects.filter(product_id=product.id, status=True)

    context = {
        "products": products,
        "reviews": reviews
    }
    return render(request, 'home.html', context)