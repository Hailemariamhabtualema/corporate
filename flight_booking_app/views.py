from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Flight, Booking, Airport, Passenger, LoyaltyMember, CorporateAccount, CorporateContact, CorporateBookingPolicy
from .forms import FlightSearchForm, BookingForm, PassengerForm, CorporateAccountRegistrationForm, CorporateContactForm, CorporateBookingPolicyForm, CorporateBookingForm, CorporatePassengerForm
from datetime import datetime, timedelta
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from .salesforce_utils import salesforce
import math
from django.contrib.auth.models import User

def home(request):
    if request.user.is_authenticated:
        airports = Airport.objects.all()
        form = FlightSearchForm()
        recent_bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')[:5]
        return render(request, 'flight_booking_app/home.html', {
            'airports': airports,
            'form': form,
            'recent_bookings': recent_bookings
        })
    else:
        account_form = CorporateAccountRegistrationForm()
        contact_form = CorporateContactForm()
        policy_form = CorporateBookingPolicyForm()
        return render(request, 'flight_booking_app/home.html', {
            'account_form': account_form,
            'contact_form': contact_form,
            'policy_form': policy_form
        })

@login_required
def search_flights(request):
    if request.method == 'GET':
        form = FlightSearchForm(request.GET)
        if form.is_valid():
            departure_airport = form.cleaned_data['departure_airport']
            arrival_airport = form.cleaned_data['arrival_airport']
            departure_date = form.cleaned_data['departure_date']
            
            flights = Flight.objects.filter(
                departure_airport=departure_airport,
                arrival_airport=arrival_airport,
                departure_time__date=departure_date,
                available_seats__gt=0
            ).order_by('departure_time')
            
            return render(request, 'flight_booking_app/flight_search.html', {
                'flights': flights,
                'form': form
            })
    else:
        form = FlightSearchForm()
    
    return render(request, 'flight_booking_app/flight_search.html', {'form': form})

def calculate_hypothetical_miles(flight):
    """
    Calculate hypothetical miles for a flight.
    If airport coordinates are available, use them. Otherwise, use the flight's distance field.
    """
    # Try to use coordinates if available
    if (flight.departure_airport.latitude is not None and 
        flight.departure_airport.longitude is not None and
        flight.arrival_airport.latitude is not None and
        flight.arrival_airport.longitude is not None):
        
        # Convert coordinates to radians
        lat1 = math.radians(float(flight.departure_airport.latitude))
        lon1 = math.radians(float(flight.departure_airport.longitude))
        lat2 = math.radians(float(flight.arrival_airport.latitude))
        lon2 = math.radians(float(flight.arrival_airport.longitude))
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        r = 3958.8  # Earth's radius in miles
        
        # Calculate distance and round to nearest 100 miles
        distance = round(c * r / 100) * 100
        return distance
    else:
        # Use the flight's distance field (convert from kilometers to miles)
        return round(float(flight.distance) * 0.621371 / 100) * 100

@login_required
def book_flight(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            number_of_passengers = form.cleaned_data['number_of_passengers']
            total_price = flight.price * number_of_passengers
            
            # Calculate miles based on flight distance
            # Convert kilometers to miles and round to nearest 100
            miles_flown = round(float(flight.distance) * 0.621371 / 100) * 100
            
            # Create booking
            booking = Booking.objects.create(
                user=request.user,
                flight=flight,
                number_of_passengers=number_of_passengers,
                total_price=total_price,
                is_confirmed=True,
                miles_earned=miles_flown  # Store miles earned in the booking
            )
            
            # Update available seats
            flight.available_seats -= number_of_passengers
            flight.save()
            
            # Create Opportunity in Salesforce and update Corporate Account
            try:
                # Create Opportunity
                opportunity_data = {
                    'Name': f'Flight Booking {booking.id}',
                    'StageName': 'Closed Won',
                    'CloseDate': datetime.now().strftime('%Y-%m-%d'),
                    'Amount': float(total_price),
                    'Description': f'Flight from {flight.departure_airport} to {flight.arrival_airport} - {miles_flown} miles earned',
                    'Type': 'Flight Booking'
                }
                salesforce.create_opportunity(opportunity_data)
                
                # Get or create Corporate Account and update points
                try:
                    account = salesforce.get_or_create_corporate_account(request.user.username)
                    account_id = account['Id']
                    current_points = float(account.get('Total_Points__c') or 0)
                    new_points = current_points + miles_flown
                    
                    # Update the account with new points
                    salesforce.update_account(account_id, {
                        'Total_Points__c': new_points
                    })
                    messages.success(request, f'Corporate Account updated with {miles_flown} new points. Total points: {new_points}')
                except Exception as e:
                    messages.warning(request, f'Error updating Corporate Account: {str(e)}')
                    
            except Exception as e:
                messages.warning(request, f'Salesforce integration failed: {str(e)}. Booking was successful.')
                print(f"Salesforce error: {str(e)}")
            
            messages.success(request, f'Booking successful! You earned {miles_flown} miles.')
            return redirect('add_passengers', booking_id=booking.id)
    else:
        form = BookingForm()
    
    return render(request, 'flight_booking_app/book_flight.html', {
        'flight': flight,
        'form': form
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
            
            # Create Contact in Salesforce
            try:
                contact_data = {
                    'FirstName': passenger.first_name,
                    'LastName': passenger.last_name,
                    'Email': form.cleaned_data.get('email', ''),
                    'Phone': form.cleaned_data.get('phone', ''),
                    'Description': f'Passenger for booking {booking.id}'
                }
                salesforce.create_contact(contact_data)
            except Exception as e:
                messages.warning(request, f'Salesforce integration failed: {str(e)}. Passenger was added successfully.')
                print(f"Salesforce error: {str(e)}")  # Log the error for debugging
            
            if booking.passengers.count() >= booking.number_of_passengers:
                return redirect('booking_detail', booking_id=booking.id)
            else:
                messages.success(request, 'Passenger added successfully. Add more passengers or complete booking.')
                return redirect('add_passengers', booking_id=booking.id)
    else:
        form = PassengerForm()
    
    return render(request, 'flight_booking_app/add_passengers.html', {
        'booking': booking,
        'form': form
    })

@login_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, 'flight_booking_app/booking_detail.html', {'booking': booking})

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
    return render(request, 'flight_booking_app/my_bookings.html', {'bookings': bookings})

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'flight_booking_app/signup.html', {'form': form})

def register_corporate_account(request):
    if request.method == 'POST':
        account_form = CorporateAccountRegistrationForm(request.POST)
        contact_form = CorporateContactForm(request.POST)
        
        if all([account_form.is_valid(), contact_form.is_valid()]):
            try:
                # Create corporate account
                account = account_form.save(commit=False)
                account.status = 'PENDING'
                account.save()
                
                # Create primary contact
                contact = contact_form.save(commit=False)
                contact.corporate_account = account
                contact.role = 'PRIMARY'
                contact.is_active = False  # Contact will be activated after review
                contact.save()
                
                # Store registration data for admin review
                registration_data = {
                    'company_name': account.name,
                    'account_type': account.account_type,
                    'address': account.address,
                    'city': account.city,
                    'annual_travel_budget': account.annual_travel_budget,
                    'contract_start_date': account.contract_start_date,
                    'contract_end_date': account.contract_end_date,
                    'contact_first_name': contact_form.cleaned_data['first_name'],
                    'contact_last_name': contact_form.cleaned_data['last_name'],
                    'contact_email': contact_form.cleaned_data['email'],
                    'contact_phone': contact_form.cleaned_data['phone'],
                    'contact_position': contact_form.cleaned_data['position'],
                    'preferred_username': contact_form.cleaned_data['username'],
                    'registration_date': datetime.now(),
                    'status': 'PENDING'
                }
                
                # Create Salesforce records without owners
                try:
                    # Create Salesforce Account
                    sf_account = salesforce.create_record('Account', {
                        'Name': account.name,
                        'Type': account.get_account_type_display(),
                        'BillingStreet': account.address,
                        'BillingCity': account.city,
                        'AnnualRevenue': float(account.annual_travel_budget),
                        'Industry': 'Transportation',
                        'Description': 'Pending corporate account registration'
                    })
                    account.salesforce_id = sf_account['id']
                    account.save()
                    
                    # Create Salesforce Contact
                    sf_contact = salesforce.create_record('Contact', {
                        'AccountId': account.salesforce_id,
                        'FirstName': contact_form.cleaned_data['first_name'],
                        'LastName': contact_form.cleaned_data['last_name'],
                        'Email': contact_form.cleaned_data['email'],
                        'Phone': contact_form.cleaned_data['phone'],
                        'Title': contact_form.cleaned_data['position'],
                        'Description': 'Primary contact for pending corporate account'
                    })
                    
                    # Create Salesforce Opportunity
                    opportunity_data = {
                        'AccountId': account.salesforce_id,
                        'Name': f'New Corporate Account - {account.name}',
                        'StageName': 'Qualification',
                        'CloseDate': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
                        'Amount': float(account.annual_travel_budget),
                        'Type': 'New Business',
                        'Description': f'New corporate account registration for {account.name}'
                    }
                    salesforce.create_record('Opportunity', opportunity_data)
                    
                except Exception as e:
                    messages.warning(request, f"Account created but Salesforce sync failed: {str(e)}")
                
                # Store registration data in session for confirmation page
                request.session['registration_data'] = {
                    'company_name': account.name,
                    'email': contact_form.cleaned_data['email']
                }
                
                messages.success(request, 'Registration submitted successfully! We will review your application and contact you soon.')
                return redirect('registration_confirmation')
                
            except Exception as e:
                messages.error(request, f'Registration failed: {str(e)}')
                return render(request, 'flight_booking_app/corporate/register.html', {
                    'account_form': account_form,
                    'contact_form': contact_form
                })
        else:
            # If forms are invalid, add error messages
            if account_form.errors:
                for field, errors in account_form.errors.items():
                    for error in errors:
                        messages.error(request, f'Account {field}: {error}')
            if contact_form.errors:
                for field, errors in contact_form.errors.items():
                    for error in errors:
                        messages.error(request, f'Contact {field}: {error}')
    else:
        account_form = CorporateAccountRegistrationForm()
        contact_form = CorporateContactForm()
    
    return render(request, 'flight_booking_app/corporate/register.html', {
        'account_form': account_form,
        'contact_form': contact_form
    })

def registration_confirmation(request):
    # Get registration data from session
    registration_data = request.session.get('registration_data', {})
    if not registration_data:
        return redirect('home')
    
    # Clear the session data after retrieving it
    request.session.pop('registration_data', None)
    
    return render(request, 'flight_booking_app/registration_confirmation.html', {
        'company_name': registration_data.get('company_name'),
        'email': registration_data.get('email')
    })

@login_required
def corporate_account_detail(request, account_id):
    account = get_object_or_404(CorporateAccount, id=account_id)
    contacts = account.corporatecontact_set.all()
    policy = account.corporatebookingpolicy_set.first()
    bookings = account.corporatebooking_set.all().order_by('-created_at')[:5]
    
    return render(request, 'flight_booking_app/corporate/detail.html', {
        'account': account,
        'contacts': contacts,
        'policy': policy,
        'recent_bookings': bookings
    })

@login_required
def update_corporate_account(request, account_id):
    account = get_object_or_404(CorporateAccount, id=account_id)
    policy = account.corporatebookingpolicy_set.first()
    
    if request.method == 'POST':
        account_form = CorporateAccountRegistrationForm(request.POST, instance=account)
        policy_form = CorporateBookingPolicyForm(request.POST, instance=policy)
        
        if all([account_form.is_valid(), policy_form.is_valid()]):
            account = account_form.save()
            policy = policy_form.save()
            
            # Update Salesforce Account
            try:
                salesforce.update_account(account.salesforce_id, {
                    'Name': account.name,
                    'Type': account.get_account_type_display(),
                    'BillingStreet': account.address,
                    'BillingCity': account.city,
                    'AnnualRevenue': float(account.annual_travel_budget)
                })
            except Exception as e:
                messages.warning(request, f"Account updated but Salesforce sync failed: {str(e)}")
            
            messages.success(request, 'Corporate account updated successfully')
            return redirect('corporate_account_detail', account_id=account.id)
    else:
        account_form = CorporateAccountRegistrationForm(instance=account)
        policy_form = CorporateBookingPolicyForm(instance=policy)
    
    return render(request, 'flight_booking_app/corporate/update.html', {
        'account_form': account_form,
        'policy_form': policy_form,
        'account': account
    })

@login_required
def add_corporate_contact(request, account_id):
    account = get_object_or_404(CorporateAccount, id=account_id)
    
    if request.method == 'POST':
        form = CorporateContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.corporate_account = account
            contact.save()
            
            # Create Salesforce Contact
            try:
                sf_contact = salesforce.create_contact({
                    'AccountId': account.salesforce_id,
                    'FirstName': contact.first_name,
                    'LastName': contact.last_name,
                    'Email': contact.email,
                    'Phone': contact.phone,
                    'Title': contact.position
                })
                contact.salesforce_id = sf_contact['id']
                contact.save()
            except Exception as e:
                messages.warning(request, f"Contact created but Salesforce sync failed: {str(e)}")
            
            messages.success(request, 'Contact added successfully')
            return redirect('corporate_account_detail', account_id=account.id)
    else:
        form = CorporateContactForm()
    
    return render(request, 'flight_booking_app/corporate/add_contact.html', {
        'form': form,
        'account': account
    })

@login_required
def corporate_booking_list(request):
    # Get all corporate accounts the user has access to
    accounts = CorporateAccount.objects.filter(corporatecontact__email=request.user.email)
    bookings = []
    
    for account in accounts:
        account_bookings = account.corporatebooking_set.all().order_by('-created_at')
        bookings.extend(account_bookings)
    
    return render(request, 'flight_booking_app/corporate/bookings.html', {
        'bookings': bookings
    })
