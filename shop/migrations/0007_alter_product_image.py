# Generated by Django 5.0.6 on 2024-12-10 12:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0006_alter_product_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=True, upload_to='uploads/%y%m%d'),
        ),
    ]
