# Generated by Django 2.1.2 on 2018-10-10 12:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Comment', '0002_auto_20181010_1254'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='commenter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='commenter_user', to=settings.AUTH_USER_MODEL),
        ),
    ]
