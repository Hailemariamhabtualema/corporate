from django.core.management.base import BaseCommand
from django.utils import timezone
from flight_booking_app.models import Flight, Route
from datetime import datetime, timedelta
import random
from decimal import Decimal

class Command(BaseCommand):
    help = 'Populate flights for all routes for the next seven days'

    def handle(self, *args, **kwargs):
        # Delete existing future flights to avoid duplicates
        future_flights = Flight.objects.filter(departure_time__gte=timezone.now())
        future_flights.delete()
        
        # Get all routes
        routes = Route.objects.all()
        
        # Generate flights for next 7 days
        for i in range(7):
            current_date = timezone.now().date() + timedelta(days=i)
            
            # For each route, create 3 flights per day
            for route in routes:
                # Morning flight (8-10 AM)
                morning_time = datetime.combine(current_date, datetime.strptime('08:00', '%H:%M').time())
                morning_time = timezone.make_aware(morning_time)
                
                # Afternoon flight (2-4 PM)
                afternoon_time = datetime.combine(current_date, datetime.strptime('14:00', '%H:%M').time())
                afternoon_time = timezone.make_aware(afternoon_time)
                
                # Evening flight (6-8 PM)
                evening_time = datetime.combine(current_date, datetime.strptime('18:00', '%H:%M').time())
                evening_time = timezone.make_aware(evening_time)
                
                flight_times = [
                    (morning_time, morning_time + route.duration),
                    (afternoon_time, afternoon_time + route.duration),
                    (evening_time, evening_time + route.duration)
                ]
                
                for dep_time, arr_time in flight_times:
                    # Generate flight number
                    flight_number = f"ET{random.randint(100, 999)}"
                    
                    # Create flight with random variation in price
                    price_variation = Decimal(str(random.uniform(0.9, 1.1)))  # ±10% variation
                    Flight.objects.create(
                        flight_number=flight_number,
                        departure_airport=route.departure_airport,
                        arrival_airport=route.arrival_airport,
                        departure_time=dep_time,
                        arrival_time=arr_time,
                        price=route.base_price * price_variation,
                        available_seats=random.randint(50, 200),
                        total_seats=200,
                        distance=route.distance,
                        base_miles=route.distance
                    )
        
        self.stdout.write(self.style.SUCCESS('Successfully populated flights for the next 7 days')) 