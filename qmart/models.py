from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from datetime import date
# Create your models7 here.

class MyUser(AbstractUser):
    phone = models.CharField(max_length=10, blank=True, unique=False)
    email = models.EmailField(max_length=50, null=False, unique=True)
    username = models.CharField(max_length=20, blank=True,unique=False, default=' ')
    REQUIRED_FIELDS = ['first_name']
    USERNAME_FIELD = "email"

class Category(models.Model):
    main_cat = models.CharField(max_length=25)
    sub_cat = models.CharField(max_length=25)


class Products(models.Model):
    prod_name = models.CharField(max_length=255, null=False)
    prod_dsc = models.TextField(max_length=500,null=False)
    prod_price = models.IntegerField(null=False)
    prod_disc = models.IntegerField(validators=[MaxValueValidator(100),MinValueValidator(0)])
    prod_avl_qty = models.IntegerField()
    pro_cat = models.ForeignKey(Category, on_delete=models.RESTRICT)


class Orders(models.Model):
    product = models.ForeignKey(Products,on_delete=models.RESTRICT)
    customer = models.ForeignKey(MyUser, on_delete=models.RESTRICT)
    odr_date  = models.DateField(default=date.today)
    ship_addr = models.TextField(max_length=510)
    ord_qty = models.IntegerField(default=1)
    status = models.CharField(max_length=2,default="OP",choices={
        "OP":"Order Placed",
        "SH":"Shipped",
        "OD":"Out for Dilevery",
        "DI":"Dilevered"
    })
    mode_of_payment = models.CharField(max_length=3,choices={
        "PPL":"Debit Card",
        "CRC":"Credit Card",
        "UPI":"Online",
        "COD":"Cash on Dilevery",
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

class Coupons(models.Model):
    code = models.CharField(max_length=5)
    count = models.IntegerField()
    discount = models.IntegerField(validators=[MaxValueValidator(100),MinValueValidator(0)])

class used_coupons(models.Model):
    cstmr_id = models.ForeignKey(MyUser,on_delete=models.RESTRICT)
    coupon = models.ForeignKey(Coupons, on_delete=models.CASCADE)