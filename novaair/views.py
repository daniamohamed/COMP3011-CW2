from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import Airport, Flight, Passenger, PaymentProvider, Booking
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import Count, F, Q
from django.shortcuts import get_object_or_404
from requests.exceptions import RequestException
from django import forms

from datetime import datetime
import json, random, string, requests

# Create your views here.

"""
Function Name: get_airports
API Endpoint handled: /airports

This function returns a list of all airports. It does not require any parameters.
"""
@csrf_exempt
@require_http_methods(["GET"])
def get_airports(request):

    try:
        list_of_airports = []
        list_of_airports = list(Airport.objects.all().values('airport_name', 'airport_code'))

        airports_list = {'status_code': 200, 'airport_list': list_of_airports}
        return JsonResponse(airports_list)

    except ObjectDoesNotExist:
        return HttpResponseBadRequest('No Airports could be found')

    except Exception as e:
        return JsonResponse({'status_code': 500, 'error': 'An error occurred: ' + str(e)}, status = 500)

"""
Function Name: get_flights
API Endpoint handled: /flights

This function retrieves appropriate flight based on the provided search parameters and returns the flight information.
"""
@csrf_exempt
@require_http_methods(["GET"])
def get_flights(request):

    try:
        source_code = request.GET.get('source')          
        destination_code = request.GET.get('destination') 
        departure_date = request.GET.get('date')

        if not all([source_code, destination_code, departure_date]):
            missing_params = [param for param in ['source', 'destination', 'date'] if request.GET.get(param) is None]
            return HttpResponseBadRequest(f" Missing required parameters: {', '.join(missing_params)}")
        
        if not Airport.objects.filter(airport_code__in=[source_code, destination_code]).count() == 2:
            return HttpResponseBadRequest('Invalid Source or Destination. Please enter a valid location.')
        
        list_of_flights = []
        flights = Flight.objects.filter(source=source_code, destination=destination_code)\
                .annotate(prev_bookings=Count('booking', filter=Q(booking__date_of_departure=departure_date)))\
                .annotate(current_capacity=F('capacity') - F('prev_bookings'))

        for flight in flights:
            list_of_flights.append({
                'flight_code': flight.flight_id,
                'duration': flight.duration,
                'flight_time': flight.time,
                'remaining_seats': flight.current_capacity,
                'business_status': flight.business,
                'eco_price': flight.eco_price,
                'bus_price': flight.bus_price
            })

        return JsonResponse({'status_code': 200, 'flight_list': list_of_flights})

    except ObjectDoesNotExist:
        return JsonResponse({'status_code': 404, 'error': 'Flight not found'})

    except Exception as e:
        return JsonResponse({'status_code': 500, 'error': str(e)})

"""
Function Name: make_booking
API Endpoint handled: /make-booking

This function handles the booking process for a specific passenger.
"""
class BookingForm(forms.Form):
    legal_name = forms.CharField()
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    date_of_birth = forms.DateField()
    passport_no = forms.CharField()
    email = forms.EmailField()
    contact_no = forms.CharField(required=False)
    flight_code = forms.CharField()
    date_of_departure = forms.DateField()
    booking_class = forms.ChoiceField(choices=[('eco', 'Economy'), ('bus', 'Business')])

@csrf_exempt
def make_booking(request):

    if request.method == 'GET':
        return HttpResponseBadRequest('GET request received. This URL only supports POST requests')
    
    try:
        form = BookingForm(request.POST)

        if not form.is_valid():
            return JsonResponse({'errors': form.errors}, status = 400)

        cleaned_data = form.cleaned_data
        dob = cleaned_data['date_of_birth']
        departure_date = cleaned_data['date_of_departure']

        if dob.year < 1950 or dob.year > 2023:
            return HttpResponseBadRequest('Invalid date of birth. Please provide a date between 1950 and 2023.')

        if departure_date.year < 2023 or dob.year > 2024:
            return HttpResponseBadRequest('Invalid date of departure. Please provide a date between 2023 and 2024.')
        
        if not Flight.objects.filter(flight_id = cleaned_data['flight_code']).exists():
            return HttpResponseBadRequest("Invalid flight code. The specified flight code does not exist.")
        
        defaults = {
            'passenger_id': ''.join(random.choices(string.ascii_uppercase + string.digits, k = 6)),
            'legal_name': cleaned_data['legal_name'],
            'first_name': cleaned_data.get('first_name', ''),
            'last_name': cleaned_data.get('last_name', ''),
            'date_of_birth': dob,
            'email': cleaned_data['email'],
            'contact_no': cleaned_data.get('contact_no', '')
        }

        passenger, created = Passenger.objects.update_or_create(
            passport_no=cleaned_data['passport_no'],
            defaults=defaults
        )

        if not created and passenger.email != cleaned_data['email']:
            return HttpResponseBadRequest('This Email ID already has a passenger. Please use a different email for your new passenger')

        booking_defaults = {
            'booking_id': ''.join(random.choices(string.ascii_uppercase + string.digits, k = 8)),
            'booking_class': cleaned_data['booking_class'],
            'invoice_id': None,
            'payment_received': False
        }

        flight = Flight.objects.get(flight_id = cleaned_data['flight_code'])

        booking, created = Booking.objects.get_or_create(
            flight_id = flight,
            passenger_id = passenger,
            date_of_departure = departure_date,
            defaults = booking_defaults
        )

        if not created:
            return HttpResponseBadRequest(f"The requested booking has been previously made with booking id {booking.booking_id}")
        
        providers = list(PaymentProvider.objects.all().values('pp_id', 'name'))
        
        return JsonResponse({'status_code': '200', 'booking_id': booking.booking_id, 'pp_list': providers})
    
    except ValidationError as e:
        return JsonResponse({'errors': str(e)}, status=400)
    
    except Exception as e:
        return JsonResponse({'errors': 'An unexpected error occurred: ' + str(e)}, status=500)
    
"""
Function Name: create_invoice
API Endpoint handled: /invoice/{booking-id}

Description:
This function handles the generation of an invoice for a specific booking. It takes the preferred vendor as a parameter and interacts with the payment provider's API endpoint to create the invoice. 
"""
@csrf_exempt
def create_invoice(request, booking_id):

    try:
        if request.method != 'POST':
            return HttpResponseBadRequest('This URL only supports POST requests')

        preferred_vendor_param = request.POST.get('preferred_vendor')

        if not preferred_vendor_param:
            return JsonResponse({'error': 'Missing required parameter: \'preferred_vendor\''}, status = 400)

        if not PaymentProvider.objects.filter(pp_id = preferred_vendor_param).exists():
            return JsonResponse({'error': '\'preferred_vendor\' is invalid'}, status = 400)

        booking = get_object_or_404(Booking, booking_id = booking_id)

        if booking.invoice_id:
            return JsonResponse({
                'error': f'Given \'booking_id\': {booking_id} already has an invoice: {booking.invoice_id}'
            }, status = 400)
        
        booking.payment_provider = PaymentProvider.objects.get(pp_id = preferred_vendor_param)
        given_provider = PaymentProvider.objects.get(pp_id = preferred_vendor_param)
        url_to_call = given_provider.url + 'invoice/'

        amount = booking.flight_id.eco_price if booking.booking_class == 'eco' else booking.flight_id.bus_price
        amount = int(amount * 100)
        input_data = {
            "api_key": '8232',
            "amount": amount,
            "metadata": []
        }

        response = requests.post(url_to_call, json = input_data)

        if response.ok:
            response_data = response.json()
            invoice_id = response_data['invoice_id']
            booking.invoice_id = invoice_id
            booking.save()

            return JsonResponse({'invoice_id': invoice_id}, status = 200)
        else:
            error_messages = {
                400: 'Bad Request',
                401: 'Unauthorized',
                403: 'Forbidden',
                404: 'Not Found',
                500: 'Internal Server Error'
            }
            error_message = error_messages.get(response.status_code, "Unknown Error")
            return JsonResponse({'error': f'Error: {error_message}'}, status = response.status_code)

    except Exception as e:
        return JsonResponse({'error': f'An error occurred: {str(e)}'}, status = 500)

"""
Function Name: invoice_status
API Endpoint handled: /confirm/{invoice-id}

Description:
This function handles the checking of the invoice status for a specific invoice. It calls the payment provider's API endpoint to retrieve the current status of the invoice. 
"""
@csrf_exempt
def invoice_status(request, booking_id):
    
    if request.method != 'POST':
        return HttpResponseBadRequest('This URL only supports POST requests')

    try:
        booking = Booking.objects.get(booking_id = booking_id)
    except Booking.DoesNotExist:
        return HttpResponseBadRequest('Invalid Booking ID.')
    except Booking.MultipleObjectsReturned:
        return HttpResponseBadRequest('Data Error: More than one booking was found for the given Booking ID.')

    provider = booking.payment_provider
    url_to_call = f'{provider.url}invoice/{booking.invoice_id}/'
    input_data = {'api_key': '8232'}

    try:
        response = requests.get(url_to_call, json = input_data)
        response.raise_for_status()  

        response_data = response.json()
        payment_status = response_data['paid']
        booking.invoice_status = payment_status
        booking.save()

        return JsonResponse({'status_code': '200', 'payment_status': payment_status})

    except RequestException as e:
        return HttpResponse(f'Error: {str(e)}')

    except (KeyError, ValueError):
        return HttpResponse('Error: Invalid response received')

    except Exception as e:
        return HttpResponse(f'Error: {str(e)}')
