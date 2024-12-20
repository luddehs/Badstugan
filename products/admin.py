from django.contrib import admin
from .models import Product, Category, ProductImage

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3

class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'sku',
        'name',
        'description',
        'price',
        'category',
        'location',
        'image',
    )
    ordering = ('sku',)
    inlines = [ProductImageInline]

class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'friendly_name',
        'name',
        'description',
    )

admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
