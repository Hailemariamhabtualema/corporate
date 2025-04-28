from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

# Create your models here.

class Airport(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

class Route(models.Model):
    departure_airport = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='departure_routes')
    arrival_airport = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='arrival_routes')
    distance = models.IntegerField()  # in kilometers
    duration = models.DurationField()  # in hours:minutes:seconds
    base_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.departure_airport.code} → {self.arrival_airport.code}"

    class Meta:
        unique_together = ('departure_airport', 'arrival_airport')

class Flight(models.Model):
    flight_number = models.CharField(max_length=10)
    departure_airport = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='departures')
    arrival_airport = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='arrivals')
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available_seats = models.IntegerField()
    total_seats = models.IntegerField()
    distance = models.DecimalField(max_digits=10, decimal_places=2, help_text="Distance in kilometers")
    base_miles = models.IntegerField(help_text="Base miles earned for this flight")

    def __str__(self):
        return f"{self.flight_number}: {self.departure_airport} to {self.arrival_airport}"

class LoyaltyProgram(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    miles_per_dollar = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)
    minimum_miles_for_reward = models.IntegerField(default=10000)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class LoyaltyMember(models.Model):
    TIER_CHOICES = [
        ('STANDARD', 'Standard'),
        ('SILVER', 'Silver'),
        ('GOLD', 'Gold'),
        ('PLATINUM', 'Platinum'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='loyalty_member')
    program = models.ForeignKey(LoyaltyProgram, on_delete=models.CASCADE)
    membership_number = models.CharField(max_length=20, unique=True)
    tier = models.CharField(max_length=10, choices=TIER_CHOICES, default='STANDARD')
    total_miles = models.IntegerField(default=0)
    miles_balance = models.IntegerField(default=0)
    join_date = models.DateField(auto_now_add=True)
    tier_expiry_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.tier} Member"

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='flight_booking_app_bookings')
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    booking_date = models.DateTimeField(auto_now_add=True)
    number_of_passengers = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_confirmed = models.BooleanField(default=False)
    miles_earned = models.IntegerField(default=0)
    loyalty_member = models.ForeignKey(LoyaltyMember, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Booking {self.id} - {self.user.username} - {self.flight}"

    def calculate_miles(self):
        if self.loyalty_member:
            base_miles = self.flight.base_miles
            tier_multiplier = {
                'STANDARD': 1.0,
                'SILVER': 1.25,
                'GOLD': 1.5,
                'PLATINUM': 2.0
            }
            multiplier = tier_multiplier[self.loyalty_member.tier]
            self.miles_earned = int(base_miles * multiplier)
            self.save()
            self.loyalty_member.total_miles += self.miles_earned
            self.loyalty_member.miles_balance += self.miles_earned
            self.loyalty_member.save()

class Passenger(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='passengers')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    passport_number = models.CharField(max_length=20)
    frequent_flyer_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class CorporateAccount(models.Model):
    ACCOUNT_TYPE_CHOICES = [
        ('SMALL', 'Small Enterprise'),
        ('MEDIUM', 'Medium Enterprise'),
        ('LARGE', 'Large Enterprise'),
        ('GOVERNMENT', 'Government Organization'),
        ('NGO', 'Non-Governmental Organization'),
    ]

    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('PENDING', 'Pending Approval'),
        ('SUSPENDED', 'Suspended'),
        ('INACTIVE', 'Inactive'),
    ]

    name = models.CharField(max_length=200)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES)
    registration_number = models.CharField(max_length=50, unique=True)
    tin_number = models.CharField(max_length=50, unique=True, verbose_name="TIN Number")
    address = models.TextField()
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='Ethiopia')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    total_points = models.IntegerField(default=0)
    contract_start_date = models.DateField()
    contract_end_date = models.DateField()
    annual_travel_budget = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_account_type_display()})"

class CorporateContact(models.Model):
    ROLE_CHOICES = [
        ('PRIMARY', 'Primary Contact'),
        ('TRAVEL_MANAGER', 'Travel Manager'),
        ('FINANCE', 'Finance Contact'),
        ('EXECUTIVE', 'Executive Contact'),
    ]

    corporate_account = models.ForeignKey(CorporateAccount, on_delete=models.CASCADE, related_name='contacts')
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    department = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    mobile = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        name = self.user.get_full_name() if self.user else f"{self.email}"
        return f"{name} - {self.get_role_display()}"

class CorporateBookingPolicy(models.Model):
    corporate_account = models.OneToOneField(CorporateAccount, on_delete=models.CASCADE, related_name='booking_policy')
    max_booking_amount = models.DecimalField(max_digits=10, decimal_places=2)
    requires_approval = models.BooleanField(default=True)
    allowed_booking_window = models.IntegerField(help_text="Maximum days in advance for booking")
    restricted_routes = models.ManyToManyField('Route', blank=True)
    preferred_routes = models.ManyToManyField('Route', related_name='preferred_by', blank=True)
    allowed_classes = models.CharField(max_length=100, help_text="Comma-separated list of allowed booking classes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Booking Policy for {self.corporate_account.name}"

class CorporateBooking(models.Model):
    APPROVAL_STATUS_CHOICES = [
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    corporate_account = models.ForeignKey(CorporateAccount, on_delete=models.CASCADE, related_name='bookings')
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    booking_date = models.DateTimeField(auto_now_add=True)
    number_of_passengers = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    miles_earned = models.IntegerField(default=0)
    approval_status = models.CharField(max_length=20, choices=APPROVAL_STATUS_CHOICES, default='PENDING')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_bookings')
    approval_date = models.DateTimeField(null=True, blank=True)
    booking_reference = models.CharField(max_length=10, unique=True)
    is_cancelled = models.BooleanField(default=False)
    cancellation_reason = models.TextField(blank=True)

    def __str__(self):
        return f"Booking {self.booking_reference} - {self.corporate_account.name}"

class CorporatePassenger(models.Model):
    booking = models.ForeignKey(CorporateBooking, on_delete=models.CASCADE, related_name='passengers')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    employee_id = models.CharField(max_length=50)
    department = models.CharField(max_length=100)
    passport_number = models.CharField(max_length=20)
    date_of_birth = models.DateField()
    frequent_flyer_number = models.CharField(max_length=20, blank=True, null=True)
    special_requests = models.TextField(blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_id})"
