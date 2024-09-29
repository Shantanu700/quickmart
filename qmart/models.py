from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from datetime import date
# Create your models7 here.

class MyUser(AbstractUser):
    phone = models.CharField(max_length=10, null=True, unique=True)
    email = models.EmailField(max_length=50, null=False, unique=True)
    REQUIRED_FIELDS = ['username','first_name','last_name']
    USERNAME_FIELD = "email"

class Category(models.Model):
    main_cat = models.CharField(max_length=25)
    sub_cat = models.CharField(max_length=25)


class Products(models.Model):
    prod_name = models.CharField(max_length=100, null=False)
    prod_dsc = models.TextField(max_length=500,null=False)
    prod_price = models.IntegerField(null=False)
    prod_disc = models.IntegerField(validators=[MaxValueValidator(100),MinValueValidator(0)])
    prod_avl_qty = models.IntegerField()
    pro_cat = models.ForeignKey(Category, on_delete=models.RESTRICT, default=1)


class Orders(models.Model):
    product = models.ForeignKey(Products,on_delete=models.RESTRICT)
    customer = models.ForeignKey(MyUser, on_delete=models.RESTRICT)
    odr_date  = models.DateField(default=date.today)
    ship_addr = models.TextField(max_length=510)
    status = models.CharField(max_length=2,default="OC",choices={
        "OC":"Order Confirmed",
        "SH":"Shipped",
        "OD":"Out for Dilevery",
        "DI":"Dilevered"
    })
    mode_of_payment = models.CharField(max_length=3,default="DC",choices={
        "DBC":"Debit Card",
        "CRC":"Credit Card",
        "UPI":"Online",
        "COD":"Cash on Dilevery",
        "NBI":"Net banking"
    })

class Cart(models.Model):
    cart_product = models.ForeignKey(Products, on_delete=models.RESTRICT)
    cart_customer = models.ForeignKey(MyUser, on_delete=models.RESTRICT)
    ord_qty = models.IntegerField()


class Images(models.Model):
    
    def get_image_path(instance, filename): 
        pro_id = instance.img_pro.pk
        # print(str(filename))
        # print(f'product_{pro_id}//{filename}')
        return f'product_{pro_id}//{filename}'
    img_pro = models.ForeignKey(Products, on_delete=models.RESTRICT)
    image = models.ImageField(max_length=500,upload_to=get_image_path)