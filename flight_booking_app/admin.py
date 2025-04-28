from django.contrib import admin
from .models import (
    Airport, Route, Flight, Booking, Passenger, LoyaltyProgram, LoyaltyMember,
    CorporateAccount, CorporateContact, CorporateBookingPolicy, CorporateBooking, CorporatePassenger
)

@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'city', 'country')
    search_fields = ('code', 'name', 'city', 'country')
    list_filter = ('country',)

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('departure_airport', 'arrival_airport', 'distance', 'duration', 'base_price')
    search_fields = ('departure_airport__code', 'arrival_airport__code')

@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ('flight_number', 'departure_airport', 'arrival_airport', 
                   'departure_time', 'arrival_time', 'price', 'available_seats')
    search_fields = ('flight_number', 'departure_airport__code', 'arrival_airport__code')
    list_filter = ('departure_airport', 'arrival_airport')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'flight', 'booking_date', 'number_of_passengers', 
                   'total_price', 'is_confirmed')
    search_fields = ('user__username', 'flight__flight_number')
    list_filter = ('is_confirmed', 'booking_date')

@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'booking', 'passport_number')
    search_fields = ('first_name', 'last_name', 'passport_number')

@admin.register(LoyaltyProgram)
class LoyaltyProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'miles_per_dollar', 'minimum_miles_for_reward', 'is_active')
    list_filter = ('is_active',)

@admin.register(LoyaltyMember)
class LoyaltyMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'membership_number', 'tier', 'total_miles', 'miles_balance')
    search_fields = ('user__username', 'membership_number')
    list_filter = ('tier',)

@admin.register(CorporateAccount)
class CorporateAccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'account_type', 'status', 'city', 'annual_travel_budget', 'total_points')
    list_filter = ('account_type', 'status', 'city')
    search_fields = ('name', 'registration_number', 'tin_number')

@admin.register(CorporateContact)
class CorporateContactAdmin(admin.ModelAdmin):
    list_display = ('corporate_account', 'role', 'email', 'phone', 'is_active')
    list_filter = ('role', 'is_active')
    search_fields = ('email', 'phone', 'first_name', 'last_name')

@admin.register(CorporateBookingPolicy)
class CorporateBookingPolicyAdmin(admin.ModelAdmin):
    list_display = ('corporate_account', 'max_booking_amount', 'requires_approval', 'allowed_booking_window')
    list_filter = ('requires_approval',)

@admin.register(CorporateBooking)
class CorporateBookingAdmin(admin.ModelAdmin):
    list_display = ('corporate_account', 'flight', 'booking_date', 'number_of_passengers', 'approval_status')
    list_filter = ('approval_status', 'is_cancelled')
    search_fields = ('booking_reference', 'corporate_account__name')

@admin.register(CorporatePassenger)
class CorporatePassengerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'employee_id', 'department', 'booking')
    search_fields = ('first_name', 'last_name', 'employee_id', 'passport_number')
