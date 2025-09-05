from django.db import models
from category.models import Category

# Create your models here.
class Product(models.Model):
    product_name     = models.CharField(max_length=100, unique=True)
    slug             = models.CharField(max_length=100, unique=True)
    descrption       = models.TextField(max_length=255, blank=True)
    price            = models.IntegerField()
    product_images   = models.ImageField(upload_to='photos/products')
    stock            = models.IntegerField()
    is_available     = models.BooleanField(default=True)
    category         = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.product_name