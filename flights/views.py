from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Flight, Booking, Airport, Passenger
from .forms import FlightSearchForm, BookingForm, PassengerForm
from datetime import datetime

def home(request):
    return render(request, 'flights/home.html')

def search_flights(request):
    form = FlightSearchForm(request.GET or None)
    flights = None
    
    if form.is_valid():
        departure_airport = form.cleaned_data['departure_airport']
        arrival_airport = form.cleaned_data['arrival_airport']
        departure_date = form.cleaned_data['departure_date']
        
        flights = Flight.objects.filter(
            departure_airport=departure_airport,
            arrival_airport=arrival_airport,
            departure_time__date=departure_date,
            available_seats__gt=0
        )
    
    return render(request, 'flights/search_flights.html', {
        'form': form,
        'flights': flights
    })

@login_required
def book_flight(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    
    if request.method == 'POST':
        booking_form = BookingForm(request.POST)
        if booking_form.is_valid():
            number_of_passengers = booking_form.cleaned_data['number_of_passengers']
            total_price = flight.price * number_of_passengers
            
            if flight.available_seats >= number_of_passengers:
                booking = Booking.objects.create(
                    user=request.user,
                    flight=flight,
                    number_of_passengers=number_of_passengers,
                    total_price=total_price
                )
                
                flight.available_seats -= number_of_passengers
                flight.save()
                
                return redirect('add_passengers', booking_id=booking.id)
            else:
                messages.error(request, 'Not enough seats available.')
    
    else:
        booking_form = BookingForm()
    
    return render(request, 'flights/book_flight.html', {
        'flight': flight,
        'form': booking_form
    })

@login_required
def add_passengers(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if request.method == 'POST':
        form = PassengerForm(request.POST)
        if form.is_valid():
            passenger = form.save(commit=False)
            passenger.booking = booking
            passenger.save()
            
            if booking.passengers.count() >= booking.number_of_passengers:
                booking.is_confirmed = True
                booking.save()
                messages.success(request, 'Booking confirmed!')
                return redirect('booking_detail', booking_id=booking.id)
            
            messages.success(request, 'Passenger added successfully.')
            return redirect('add_passengers', booking_id=booking.id)
    
    else:
        form = PassengerForm()
    
    return render(request, 'flights/add_passengers.html', {
        'booking': booking,
        'form': form,
        'remaining_passengers': booking.number_of_passengers - booking.passengers.count()
    })

@login_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, 'flights/booking_detail.html', {'booking': booking})

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
    return render(request, 'flights/my_bookings.html', {'bookings': bookings}) 