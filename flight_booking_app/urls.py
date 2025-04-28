from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search_flights, name='search_flights'),
    path('book/<int:flight_id>/', views.book_flight, name='book_flight'),
    path('booking/<int:booking_id>/add-passengers/', views.add_passengers, name='add_passengers'),
    path('booking/<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('signup/', views.signup, name='signup'),
    path('corporate/register/', views.register_corporate_account, name='register_corporate_account'),
    path('corporate/registration-confirmation/', views.registration_confirmation, name='registration_confirmation'),
    path('corporate/account/<int:account_id>/', views.corporate_account_detail, name='corporate_account_detail'),
    path('corporate/account/<int:account_id>/update/', views.update_corporate_account, name='update_corporate_account'),
    path('corporate/account/<int:account_id>/add-contact/', views.add_corporate_contact, name='add_corporate_contact'),
    path('corporate/bookings/', views.corporate_booking_list, name='corporate_booking_list'),
] 