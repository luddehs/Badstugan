# Generated by Django 4.2.9 on 2024-11-26 15:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_product_capacity'),
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('time_slot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to='products.timeslot')),
            ],
        ),
    ]
