# Generated by Django 5.0.6 on 2024-12-02 17:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='attempts',
        ),
    ]