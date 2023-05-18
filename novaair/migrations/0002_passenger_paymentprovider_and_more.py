# Generated by Django 4.0.3 on 2023-05-14 19:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('novaair', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Passenger',
            fields=[
                ('passenger_id', models.CharField(max_length=6, primary_key=True, serialize=False)),
                ('legal_name', models.CharField(max_length=255)),
                ('first_name', models.CharField(blank=True, max_length=255, null=True)),
                ('last_name', models.CharField(blank=True, max_length=255, null=True)),
                ('date_of_birth', models.DateField()),
                ('passport_no', models.CharField(max_length=9, unique=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('contact_no', models.CharField(blank=True, max_length=12, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PaymentProvider',
            fields=[
                ('pp_id', models.CharField(max_length=3, primary_key=True, serialize=False)),
                ('url', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.RenameField(
            model_name='airport',
            old_name='airportCode',
            new_name='airport_code',
        ),
        migrations.RenameField(
            model_name='airport',
            old_name='airportName',
            new_name='airport_name',
        ),
        migrations.CreateModel(
            name='Flight',
            fields=[
                ('flight_id', models.CharField(max_length=6, primary_key=True, serialize=False)),
                ('capacity', models.PositiveSmallIntegerField()),
                ('duration', models.PositiveSmallIntegerField()),
                ('time', models.PositiveSmallIntegerField()),
                ('business', models.BooleanField()),
                ('eco_price', models.FloatField()),
                ('bus_price', models.FloatField(blank=True, null=True)),
                ('destination', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='arrivals', to='novaair.airport')),
                ('source', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='departures', to='novaair.airport')),
            ],
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('booking_id', models.CharField(max_length=8, primary_key=True, serialize=False)),
                ('date_of_departure', models.DateField()),
                ('booking_class', models.CharField(choices=[('eco', 'Economy'), ('bus', 'Business')], max_length=3)),
                ('invoice_id', models.IntegerField(null=True)),
                ('payment_received', models.BooleanField(default=False)),
                ('flight_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='novaair.flight')),
                ('passenger_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='novaair.passenger')),
                ('payment_provider', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='novaair.paymentprovider')),
            ],
        ),
    ]
