# Flight Booking System

A Django-based web application for booking flights. This system allows users to search for flights, make bookings, and manage their reservations.

## Features

- User authentication (login/signup)
- Flight search with filters
- Flight booking system
- Passenger management
- Booking history
- Admin interface for managing flights and bookings

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd flight-booking-system
```

2. Create and activate a virtual environment:
```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Apply database migrations:
```bash
python manage.py migrate
```

5. Create a superuser for admin access:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

## Usage

1. Access the application at `http://127.0.0.1:8000/`
2. Create an account or log in
3. Search for flights using the search form
4. Select a flight and proceed with booking
5. Add passenger details
6. Confirm the booking

## Admin Interface

Access the admin interface at `http://127.0.0.1:8000/admin/` using your superuser credentials to:
- Manage airports
- Add/edit flights
- View and manage bookings
- Manage passengers

## Project Structure

```
flight_booking/
├── flights/
│   ├── migrations/
│   ├── templates/
│   │   └── flights/
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── flight_booking/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
└── requirements.txt
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 