from django.core.exceptions import ValidationError
from django.contrib import admin
from django.db import models
from .models import Product, Category, ProductImage, TimeSlot
from .utils import generate_time_slots
from datetime import datetime, timedelta
from django.utils import timezone
from django.shortcuts import render

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
    actions = ['generate_future_slots']

    def generate_future_slots(self, request, queryset):
        from django.core.exceptions import ValidationError
        from django import forms
        
        # Get the latest existing time slot for reference
        latest_slots = {
            product: product.time_slots.order_by('-end_time').first()
            for product in queryset
        }
        
        # If no slots exist, start from tomorrow
        start_dates = {
            product: (latest_slots[product].end_time.date() + timedelta(days=1))
            if latest_slots[product]
            else (timezone.now().date() + timedelta(days=1))
            for product in queryset
        }

        class WeeksForm(forms.Form):
            _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
            weeks = forms.IntegerField(min_value=1, max_value=52, initial=2,
                                     help_text="Number of weeks to generate slots for")

        if 'apply' in request.POST:
            form = WeeksForm(request.POST)
            if form.is_valid():
                weeks = form.cleaned_data['weeks']
                slots_created = 0
                
                for product in queryset:
                    if product.category and product.category.name == 'shared-sauna':
                        start_date = start_dates[product]
                        end_date = start_date + timedelta(weeks=weeks)
                        
                        generate_time_slots(product, start_date, end_date)
                        slots_created += 1
                
                self.message_user(
                    request,
                    f'Generated {weeks} weeks of timeslots for {slots_created} products, starting from their last slot'
                )
                return
                
        form = WeeksForm(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})
        return render(
            request,
            'admin/generate_slots.html',
            context={
                'title': 'Generate future timeslots',
                'form': form,
                'queryset': queryset,
                'start_dates': start_dates
            }
        )
    generate_future_slots.short_description = "Generate future timeslots"

class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'friendly_name',
        'name',
        'description',
    )

class TimeSlotAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'start_time',
        'end_time',
        'duration_display',
        'is_booked',
        'is_past',
        'remaining_capacity'
    )
    list_filter = ('product', 'is_booked', 'start_time')
    search_fields = ('product__name',)
    ordering = ('start_time',)
    
    def remaining_capacity(self, obj):
        total_bookings = obj.bookings.aggregate(
            total=models.Sum('quantity'))['total'] or 0
        return obj.product.capacity - total_bookings
    remaining_capacity.short_description = 'Remaining Capacity'

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
