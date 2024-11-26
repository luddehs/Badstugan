from django.core.exceptions import ValidationError
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
        'category',
        'price',
        'capacity',
        'session_limit',
        'location',
    )
    ordering = ('sku',)
    inlines = [ProductImageInline, TimeSlotInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('sku', 'name', 'description', 'category', 'price', 'location')
        }),
        ('Capacity Settings', {
            'fields': ('capacity', 'session_limit'),
            'description': 'Set total capacity and per-session booking limits'
        }),
        ('Images', {
            'fields': ('image_url', 'image')
        }),
    )

class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'friendly_name',
        'name',
        'description',
    )

class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('product', 'start_time', 'end_time', 'duration_display', 'is_booked', 'is_past', 'has_conflicts')
    list_filter = ('product', 'is_booked', 'start_time')
    search_fields = ('product__name',)
    ordering = ('start_time',)
    list_editable = ('is_booked',)
    readonly_fields = ('is_past', 'duration_display', 'has_conflicts')

    def duration_display(self, obj):
        hours = obj.duration.total_seconds() / 3600
        return f"{hours:.1f} hours"
    duration_display.short_description = 'Duration'

    def has_conflicts(self, obj):
        return obj.has_conflict()
    has_conflicts.boolean = True
    has_conflicts.short_description = 'Has Conflicts'

    def save_model(self, request, obj, form, change):
        try:
            obj.clean()
            super().save_model(request, obj, form, change)
        except ValidationError as e:
            form.add_error(None, e)

admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(TimeSlot, TimeSlotAdmin)
