import pytest
import requests
import requests_mock

'''
To run the tests:
1. cd novaair
2. pytest -v test.py
'''


def test_make_booking():

    url = 'http://127.0.0.1:3360/novaair/make-booking/'

    payload_booking = {
        'legal_name': 'Aaron Ramsdale',
        'first_name': 'Aaron',
        'last_name': 'Ramsdale',
        'date_of_birth': '1999-03-26',
        'passport_no': 'AR1826492',
        'email': 'aaron@arsenal.co.uk',
        'contact_no': '27464657563',
        'flight_code': 'NA09',
        'date_of_departure': '2023-07-15',
        'booking_class': 'bus'
    }

    response = requests.post(url, data=payload_booking)

    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}, response content: {response.content}"
    
    response_json = response.json()
    assert 'booking_id' in response_json, f"Expected 'booking_id' in response, but got {response.text}"


def test_invoice():
    
    url = 'http://127.0.0.1:3360/novaair/invoice/DAZ2OWOJ/'

    payload_invoice = {
        'preferred_vendor': 'NN7'
    }

    response = requests.post(url, data = payload_invoice)

    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}, response content: {response.content}"
    
    response_json = response.json()
    assert 'invoice_id' in response_json, f"Expected 'invoice_id' in response, but got {response.text}"

def test_invoice_status():
    
    url = 'http://127.0.0.1:3360/novaair/confirm/DAZ2OWOJ/'

    response = requests.post(url)

    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}, response content: {response.content}"
    
    response_json = response.json()
    assert 'payment_status' in response_json, f"Expected 'payment_status' in response, but got {response.text}"