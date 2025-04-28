from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('flight_booking_app', '0003_corporate_models'),
    ]

    operations = [
        migrations.AddField(
            model_name='corporatecontact',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='corporatecontact',
            name='mobile',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ] 