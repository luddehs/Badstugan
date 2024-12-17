from django.core.management.base import BaseCommand
from products.models import Product
from products.utils import generate_time_slots
from datetime import datetime, timedelta
from django.utils import timezone

class Command(BaseCommand):
    help = 'Generate timeslots for shared saunas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Number of days to generate slots for'
        )

    def handle(self, *args, **options):
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=options['days'])
        
        saunas = Product.objects.filter(
            category__name__in=['shared-sauna', 'private-sauna']
        )
        
        for product in saunas:
            generate_time_slots(product, start_date, end_date)
            self.stdout.write(
                self.style.SUCCESS(f'Generated slots for {product.name}')
            ) 