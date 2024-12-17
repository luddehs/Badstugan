from datetime import datetime, timedelta
from django.utils import timezone
from .models import TimeSlot

def generate_time_slots(product, start_date, end_date=None, slot_duration=timedelta(hours=2)):
    """
    Generate timeslots for a product within the category's opening hours
    """
    if not end_date:
        end_date = start_date

    current_date = start_date
    while current_date <= end_date:
        # Get opening hours for this date
        opening_time, closing_time = product.category.get_opening_hours(current_date)
        
        # Combine date and time
        current_datetime = timezone.make_aware(
            datetime.combine(current_date, opening_time)
        )
        end_datetime = timezone.make_aware(
            datetime.combine(current_date, closing_time)
        )

        # Generate slots for this day
        while current_datetime + slot_duration <= end_datetime:
            # Check if slot already exists
            existing_slot = TimeSlot.objects.filter(
                product=product,
                start_time=current_datetime,
                end_time=current_datetime + slot_duration
            ).exists()

            if not existing_slot:
                TimeSlot.objects.create(
                    product=product,
                    start_time=current_datetime,
                    end_time=current_datetime + slot_duration
                )
            
            current_datetime += slot_duration
        
        current_date += timedelta(days=1) 