from django.urls import path
from . import views

# API
urlpatterns = [
    path('airports/', views.get_airports, name='get_airports'),
    path('flights/', views.get_flights, name='get_flights'),
    path('make-booking/', views.make_booking, name='make_booking'),
    path('invoice/<str:booking_id>/', views.create_invoice, name='create_invoice'),
    path('confirm/<str:booking_id>/', views.invoice_status, name='invoice_status')
]