# Generated by Django 5.0 on 2024-09-23 16:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qmart', '0007_delete_images'),
    ]

    operations = [
        migrations.CreateModel(
            name='Images',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(max_length=500, upload_to='Cars/')),
                ('img_pro', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='qmart.products')),
            ],
        ),
    ]
