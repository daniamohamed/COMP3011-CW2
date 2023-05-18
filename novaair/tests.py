from django.test import TestCase, Client
from django.urls import reverse
from .models import Airport
from .models import Airport, Flight, Passenger, PaymentProvider, Booking

# Create your tests here.

class NovaAirTests(TestCase):

    def main(self):
        self.client = Client()

    def test_get_airports(self):
        
        Airport.objects.create(airport_name = 'Test Airport 1', airport_code = 'TA1')
        Airport.objects.create(airport_name = 'Test Airport 2', airport_code = 'TA2')

        response = self.client.get(reverse('get_airports'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['airport_list']), 2)
    
    def test_get_flights(self):
    
        airport1 = Airport.objects.create(airport_name = 'Test Airport 1', airport_code = 'TAA')
        airport2 = Airport.objects.create(airport_name = 'Test Airport 2', airport_code = 'TAB')
    
        Flight.objects.create(
            flight_id = 'NAT1',
            capacity = 100,
            source = airport1,
            destination = airport2,
            duration = 1200,
            time = 1245,
            business = True,
            eco_price = 100,
            bus_price = 200
        )
        Flight.objects.create(
            flight_id = 'NAT2',
            capacity = 100,
            source = airport1,
            destination = airport2,
            duration = 1800,
            time = 1530,
            business = True,
            eco_price = 150,
            bus_price = 300
        )
    
        departure_date = '2023-07-12'
        response = self.client.get(reverse('get_flights'), {'source': 'TAA', 'destination': 'TAB', 'date': departure_date})
    
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['flight_list']), 2)
    
        for flight in response.json()['flight_list']:
            self.assertIn(flight['flight_code'], ['NAT1', 'NAT2'])
    
    def test_make_booking(self):

        airport1 = Airport.objects.create(airport_name = 'Test Airport 1', airport_code = 'TAA')
        airport2 = Airport.objects.create(airport_name = 'Test Airport 2', airport_code = 'TAB')
        flight = Flight.objects.create(flight_id = 'NAT1', capacity = 200, source = airport1, destination = airport2,
                                            duration = 1200, time = 1040, business = True, eco_price = 145, bus_price=420)
        payment_provider = PaymentProvider.objects.create(pp_id = 'PP1', url='http://payment.com', name = 'Test PP')

        payload_booking = {
            'legal_name': 'John Doe',
            'first_name': 'John',
            'last_name': 'Doe',
            'date_of_birth': '1999-10-04',
            'passport_no': 'JD6728372',
            'email': 'johndoe@gmail.com',
            'contact_no': '9876567890',
            'flight_code': 'NAT1',
            'date_of_departure': '2023-07-11',
            'booking_class': 'bus'
        }

        response = self.client.post(reverse('make_booking'), data = payload_booking)

        if response.status_code != 200:
            print(response.content)

        self.assertEqual(response.status_code, 200)

        response_content = response.json()
        self.assertIn('booking_id', response_content)
        self.assertIn('pp_list', response_content)

        booking_id = response_content['booking_id']
        self.assertTrue(Booking.objects.filter(booking_id = booking_id).exists())



