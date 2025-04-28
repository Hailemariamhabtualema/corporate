from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Airport, Booking, Passenger, CorporateAccount, CorporateContact, CorporateBookingPolicy, CorporateBooking, CorporatePassenger
from datetime import datetime

class FlightSearchForm(forms.Form):
    departure_airport = forms.ModelChoiceField(
        queryset=Airport.objects.all(),
        empty_label="Select Departure Airport",
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Departure Airport"
    )
    arrival_airport = forms.ModelChoiceField(
        queryset=Airport.objects.all(),
        empty_label="Select Arrival Airport",
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Arrival Airport"
    )
    departure_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label="Departure Date"
    )

    def clean(self):
        cleaned_data = super().clean()
        departure_airport = cleaned_data.get('departure_airport')
        arrival_airport = cleaned_data.get('arrival_airport')

        if departure_airport and arrival_airport and departure_airport == arrival_airport:
            raise forms.ValidationError("Departure and arrival airports cannot be the same.")

        return cleaned_data

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['number_of_passengers']
        widgets = {
            'number_of_passengers': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '9'
            })
        }

class PassengerForm(forms.ModelForm):
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Passenger
        fields = ['first_name', 'last_name', 'date_of_birth', 'passport_number']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'passport_number': forms.TextInput(attrs={'class': 'form-control'})
        }

class CorporateAccountRegistrationForm(forms.ModelForm):
    class Meta:
        model = CorporateAccount
        fields = ['name', 'account_type', 'address', 'city', 'annual_travel_budget', 'contract_start_date', 'contract_end_date']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company Name'}),
            'account_type': forms.Select(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Company Address'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'annual_travel_budget': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Annual Travel Budget'}),
            'contract_start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'contract_end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make registration_number and tin_number optional
        self.fields['registration_number'] = forms.CharField(
            required=False,
            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Registration Number'})
        )
        self.fields['tin_number'] = forms.CharField(
            required=False,
            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'TIN Number'})
        )

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Set default values for registration_number and tin_number if not provided
        if not instance.registration_number:
            instance.registration_number = f"TEMP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        if not instance.tin_number:
            instance.tin_number = f"TIN-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        if commit:
            instance.save()
        return instance

class CorporateContactForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Preferred Username'})
    )
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    position = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Job Position'})
    )

    class Meta:
        model = CorporateContact
        fields = ['phone', 'mobile', 'email', 'department']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Number (Optional)'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Department'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make mobile field optional
        self.fields['mobile'].required = False
        # Make other fields required
        required_fields = ['username', 'first_name', 'last_name', 'position', 'phone', 'email', 'department']
        for field in required_fields:
            self.fields[field].required = True

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Set role to PRIMARY for new contacts
        instance.role = 'PRIMARY'
        if commit:
            instance.save()
        return instance

class CorporateBookingPolicyForm(forms.ModelForm):
    class Meta:
        model = CorporateBookingPolicy
        fields = ['max_booking_amount', 'requires_approval', 'allowed_booking_window', 'allowed_classes']
        widgets = {
            'max_booking_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'requires_approval': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'allowed_booking_window': forms.NumberInput(attrs={'class': 'form-control'}),
            'allowed_classes': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        requires_approval = cleaned_data.get('requires_approval')
        approval_threshold = cleaned_data.get('approval_threshold')
        
        if requires_approval and not approval_threshold:
            raise forms.ValidationError("Approval threshold is required when approval is enabled")
        
        return cleaned_data

class CorporateBookingForm(forms.ModelForm):
    class Meta:
        model = CorporateBooking
        fields = ['number_of_passengers']

class CorporatePassengerForm(forms.ModelForm):
    class Meta:
        model = CorporatePassenger
        fields = ['first_name', 'last_name', 'employee_id', 'department',
                 'passport_number', 'date_of_birth', 'frequent_flyer_number',
                 'special_requests']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        } 