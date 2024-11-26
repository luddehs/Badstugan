from django.contrib import admin
from .models import Product, Category, ProductImage, TimeSlot

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3

class TimeSlotInline(admin.TabularInline):
    model = TimeSlot
    extra = 1
    fields = ('start_time', 'end_time', 'is_booked')
    ordering = ('start_time',)

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
    inlines = [ProductImageInline, TimeSlotInline]

class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'friendly_name',
        'name',
        'description',
    )

class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('product', 'start_time', 'end_time', 'is_booked', 'is_past')
    list_filter = ('product', 'is_booked', 'start_time')
    search_fields = ('product__name',)
    ordering = ('start_time',)
    list_editable = ('is_booked',)
    readonly_fields = ('is_past',)

    def is_past(self, obj):
        if not obj or not obj.start_time:
            return False
        return obj.is_past
    is_past.boolean = True
    is_past.short_description = 'Past Time Slot'

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.is_past:
            return self.readonly_fields + ('start_time', 'end_time')
        return self.readonly_fields

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Make start_time and end_time required
        form.base_fields['start_time'].required = True
        form.base_fields['end_time'].required = True
        return form

admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(TimeSlot, TimeSlotAdmin)
