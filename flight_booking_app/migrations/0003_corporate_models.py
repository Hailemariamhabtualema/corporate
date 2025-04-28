from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('flight_booking_app', '0002_route'),
    ]

    operations = [
        migrations.CreateModel(
            name='CorporateAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('account_type', models.CharField(choices=[('SMALL', 'Small Enterprise'), ('MEDIUM', 'Medium Enterprise'), ('LARGE', 'Large Enterprise'), ('GOVERNMENT', 'Government Organization'), ('NGO', 'Non-Governmental Organization')], max_length=20)),
                ('registration_number', models.CharField(max_length=50, unique=True)),
                ('tin_number', models.CharField(max_length=50, unique=True, verbose_name='TIN Number')),
                ('address', models.TextField()),
                ('city', models.CharField(max_length=100)),
                ('country', models.CharField(default='Ethiopia', max_length=100)),
                ('status', models.CharField(choices=[('ACTIVE', 'Active'), ('PENDING', 'Pending Approval'), ('SUSPENDED', 'Suspended'), ('INACTIVE', 'Inactive')], default='PENDING', max_length=20)),
                ('total_points', models.IntegerField(default=0)),
                ('contract_start_date', models.DateField()),
                ('contract_end_date', models.DateField()),
                ('annual_travel_budget', models.DecimalField(decimal_places=2, max_digits=12)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='CorporateContact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('PRIMARY', 'Primary Contact'), ('TRAVEL_MANAGER', 'Travel Manager'), ('FINANCE', 'Finance Contact'), ('EXECUTIVE', 'Executive Contact')], max_length=20)),
                ('department', models.CharField(max_length=100)),
                ('phone', models.CharField(max_length=20)),
                ('mobile', models.CharField(max_length=20)),
                ('email', models.EmailField(max_length=254)),
                ('is_active', models.BooleanField(default=True)),
                ('corporate_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contacts', to='flight_booking_app.corporateaccount')),
            ],
        ),
        migrations.CreateModel(
            name='CorporateBookingPolicy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('max_booking_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('requires_approval', models.BooleanField(default=True)),
                ('allowed_booking_window', models.IntegerField(help_text='Maximum days in advance for booking')),
                ('allowed_classes', models.CharField(help_text='Comma-separated list of allowed booking classes', max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('corporate_account', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='booking_policy', to='flight_booking_app.corporateaccount')),
                ('preferred_routes', models.ManyToManyField(blank=True, related_name='preferred_by', to='flight_booking_app.route')),
                ('restricted_routes', models.ManyToManyField(blank=True, to='flight_booking_app.route')),
            ],
        ),
        migrations.CreateModel(
            name='CorporateBooking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('booking_date', models.DateTimeField(auto_now_add=True)),
                ('number_of_passengers', models.IntegerField()),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('miles_earned', models.IntegerField(default=0)),
                ('approval_status', models.CharField(choices=[('PENDING', 'Pending Approval'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected')], default='PENDING', max_length=20)),
                ('approval_date', models.DateTimeField(blank=True, null=True)),
                ('booking_reference', models.CharField(max_length=10, unique=True)),
                ('is_cancelled', models.BooleanField(default=False)),
                ('cancellation_reason', models.TextField(blank=True)),
                ('corporate_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to='flight_booking_app.corporateaccount')),
                ('flight', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='flight_booking_app.flight')),
            ],
        ),
        migrations.CreateModel(
            name='CorporatePassenger',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('employee_id', models.CharField(max_length=50)),
                ('department', models.CharField(max_length=100)),
                ('passport_number', models.CharField(max_length=20)),
                ('date_of_birth', models.DateField()),
                ('frequent_flyer_number', models.CharField(blank=True, max_length=20, null=True)),
                ('special_requests', models.TextField(blank=True)),
                ('booking', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='passengers', to='flight_booking_app.corporatebooking')),
            ],
        ),
    ] 