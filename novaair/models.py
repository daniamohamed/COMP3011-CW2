from django.db import models

# Create your models here.

# Model representing an Airport
class Airport(models.Model):
    airport_code = models.CharField(max_length = 3, primary_key = True)
    airport_name = models.CharField(max_length = 255)

    def __str__(self):
      return f'{self.airport_name} ({self.airport_code})'

# Model representing a Flight
class Flight(models.Model):
    flight_id = models.CharField(max_length = 4, primary_key = True)
    capacity = models.PositiveSmallIntegerField()
    source = models.ForeignKey(Airport, to_field = 'airport_code', on_delete = models.PROTECT, related_name = 'departures')
    destination = models.ForeignKey(Airport, to_field = 'airport_code', on_delete = models.PROTECT, related_name='arrivals')
    duration = models.PositiveSmallIntegerField()
    time = models.PositiveSmallIntegerField()
    business = models.BooleanField()
    eco_price = models.FloatField()
    bus_price = models.FloatField(blank = True, null = True)
    
    def __str__(self):
      return f'Flight ID {self.flight_id}: {self.source} - {self.destination}, Departure Time (24h): {self.time}, Duration: {self.duration} minutes'

# Model representing a Passenger
class Passenger(models.Model):
    passenger_id = models.CharField(max_length = 6, primary_key = True)
    legal_name = models.CharField(max_length = 255)
    first_name = models.CharField(max_length = 255, blank = True, null = True)
    last_name = models.CharField(max_length = 255, blank = True, null = True)
    date_of_birth = models.DateField()
    passport_no = models.CharField(max_length = 9, unique = True)
    email = models.EmailField(unique = True)
    contact_no = models.CharField(max_length = 12, blank = True, null = True)
    
    def __str__(self):
        return f'Legal Name: {self.legal_name} - Passport Number: ({self.passport_no}, Email ID: ({self.email}), Contact Number: ({self.contact_no})'

# Model representing a Payment Provider
class PaymentProvider(models.Model):
    """Model representing a Payment Provider"""
    pp_id = models.CharField(max_length = 3, primary_key = True)
    url = models.CharField(max_length = 255)
    name = models.CharField(max_length = 255)

    def __str__(self):
      
      return f'Payment Provider: {self.name} - ID: {self.pp_id}'

# Model representing a Booking
class Booking(models.Model):
    booking_id = models.CharField(max_length = 8, primary_key = True)
    flight_id = models.ForeignKey(Flight, to_field = 'flight_id', on_delete = models.PROTECT)
    passenger_id = models.ForeignKey(Passenger, to_field = 'passenger_id', on_delete = models.PROTECT)
    date_of_departure = models.DateField()
    booking_class = models.CharField(max_length = 3, choices = [('eco', 'Economy'),('bus', 'Business')])
    payment_provider = models.ForeignKey(PaymentProvider, to_field = 'pp_id', on_delete = models.PROTECT, null = True)
    invoice_id = models.IntegerField(null = True)
    payment_received = models.BooleanField(default = False)

    def __str__(self):
        return f'Booking ID: {self.booking_id} - Flight ID: {self.flight_id.flight_id}, Passenger ID: {self.passenger_id.legal_name} ({self.booking_class}) , Invoice ID: {self.invoice_id}'