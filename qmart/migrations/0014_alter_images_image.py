# Generated by Django 5.0 on 2024-09-26 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qmart', '0013_alter_products_prod_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='images',
            name='image',
            field=models.ImageField(max_length=500, upload_to=None),
        ),
    ]
