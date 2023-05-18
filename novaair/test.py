import pytest
import requests

'''
To run the tests:
1. cd novaair
2. pytest -v test.py
'''

# Test for make_booking()
def test_make_booking():

    url = 'http://127.0.0.1:3360/novaair/make-booking/'

    payload_booking = {
        'legal_name': 'Gabriel Jesus',
        'first_name': 'Gabriel',
        'last_name': 'Jesus',
        'date_of_birth': '1995-06-26',
        'passport_no': 'GJ1829074',
        'email': 'gabijesus@arsenal.co.uk',
        'contact_no': '27507623563',
        'flight_code': 'NA05',
        'date_of_departure': '2023-07-15',
        'booking_class': 'bus'
    }

    response = requests.post(url, data=payload_booking)

    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}, response content: {response.content}"
    
    response_json = response.json()
    assert 'booking_id' in response_json, f"Expected 'booking_id' in response, but got {response.text}"

# Test for create_invoice()
def test_invoice():
    
    url = 'http://127.0.0.1:3360/novaair/invoice/BZRR03XJ/'

    payload_invoice = {
        'preferred_vendor': 'NN7'
    }

    response = requests.post(url, data = payload_invoice)

    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}, response content: {response.content}"
    
    response_json = response.json()
    assert 'invoice_id' in response_json, f"Expected 'invoice_id' in response, but got {response.text}"

# Test for invoice_status()
def test_invoice_status():
    
    url = 'http://127.0.0.1:3360/novaair/confirm/BZRR03XJ/'

    response = requests.post(url)

    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}, response content: {response.content}"
    
    response_json = response.json()
    assert 'payment_status' in response_json, f"Expected 'payment_status' in response, but got {response.text}"