# Generated by Django 2.1.2 on 2018-10-11 12:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Comment', '0013_auto_20181011_1025'),
        ('Announcement', '0004_announcement_classroom'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='announcement',
            name='comment',
        ),
        migrations.AddField(
            model_name='announcement',
            name='comment',
            field=models.ManyToManyField(related_name='announcement', to='Comment.Comment'),
        ),
    ]
