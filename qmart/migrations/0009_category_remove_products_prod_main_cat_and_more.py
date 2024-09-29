# Generated by Django 5.0 on 2024-09-24 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qmart', '0008_images'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('main_cat', models.CharField(max_length=10)),
                ('sub_cat', models.CharField(max_length=10)),
            ],
        ),
        migrations.RemoveField(
            model_name='products',
            name='prod_main_cat',
        ),
        migrations.RemoveField(
            model_name='products',
            name='prod_rating',
        ),
        migrations.RemoveField(
            model_name='products',
            name='prod_sub_cat',
        ),
    ]
