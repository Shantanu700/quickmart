from django.db import IntegrityError
from django.http import JsonResponse
import json
import re
from qmart.models import *
from django.contrib.auth import authenticate, login, logout

# Create your views here.


def register(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            first_name = data['Fname']
            if not first_name.isalpha():
                return JsonResponse({"Err":"Invalid First name, should be in alphabets"}, status=422)
            u_name = data['Uname']
            if not u_name.isalnum():
                return JsonResponse({"Err":"Invalid User name, should be in alphabets or digits"}, status=422)
            l_name = data['Lname']
            if not l_name.isalpha():
                return JsonResponse({"Err":"Invalid Last name, should be in alphabets"}, status=422)
            e_mail = data['Email']
            if not bool(re.match(r"[a-zA-Z0-9_\-\.]+[@][a-z]+[\.][a-z]{2,3}",e_mail)):
                return JsonResponse({"Err":"Invalid Email, should in the form abc@xyz.com"},status=422)
            mobile = data['Mobile']
            if not (mobile.isnumeric() and len(mobile) == 10) or (not mobile):
                return JsonResponse({"Err":"Invalid Phone, shoud be of 10 digits and numeric"},status=422)
            passwd_1 = data['Passwd1']
            passwd_2 = data['Passwd2']
            if not bool(re.match(r"^(?=.*[A-Z])(?=.*[!@#$&*])(?=.*[0-9])(?=.*[a-z]).{8,16}$",passwd_1)):
                return JsonResponse({"Err":"Weak Password, should include an upper case, a number and an special Symbol"},status=400)
            if not passwd_1 == passwd_2:
                return JsonResponse({"Err":"passwords do not match"}, status=409)
            new_user = MyUser.objects.create_user(u_name, e_mail, passwd_1,first_name=first_name,last_name = l_name,phone = mobile)
            new_user.save()
            return JsonResponse({'status': 'success', 'f_name': first_name, 'u_name': u_name, 'l_name': l_name, },status=201)
        except IntegrityError as I:
            return JsonResponse({"Err":I.args[1]}, status=409)
    return JsonResponse({"Err":"Invalid request method"},status=405) 

def signin(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print(data)
        e_mail = data['Email']
        passwd = data['Passwd']
        if e_mail in [user.email for user in MyUser.objects.all()]:
            User = authenticate(email=e_mail,password=passwd)
            if User is not None:
                login(request,User)
                return JsonResponse({"status":"Logged in Successfully", "is_admin": User.is_superuser},status=200 )
            return JsonResponse({"Err":"Password entered is incorrect"},status=400)
        return JsonResponse({"Err":"No user with these credentials"},status=400)
    return JsonResponse({"Err":"Invalid request method"},status=405)

def info(request):
    if request.method == 'GET':
        dict = {"Category" : {cat['main_cat'] : [sub.sub_cat for sub in Category.objects.filter(main_cat=cat['main_cat'])] for cat in Category.objects.values('main_cat').distinct()  } }
        if request.user.is_authenticated:
            dict['first_name'] = request.user.first_name
            dict["is_admin"] = request.user.is_superuser
            return JsonResponse(dict)
        return JsonResponse(dict)
    return JsonResponse({"Err":"Invalid request method"},status=405)
            

def signout(request):
    if request.method == 'POST':
        if request.user is not None:
            if request.user.is_authenticated:
                print((request.user))
                logout(request)
                return JsonResponse({"status":"Logged out Successfully"},status=200 )
            return JsonResponse({"Err":"No any User was autherized"},status=400)
        return JsonResponse({"Err":"No any User"},status=400)
    return JsonResponse({"Err":"Invalid request method"},status=405)

def show_prod(request):    
    if request.method == 'GET':
        prods = list({"id":pro.id,
                      "title":pro.prod_name,
                      "price":pro.prod_price,
                      "discount":pro.prod_disc,
                      "description":pro.prod_dsc,
                      "available_qty":pro.prod_avl_qty,
                      "main_category":pro.pro_cat.main_cat,
                      "sub_category":pro.pro_cat.sub_cat,
                      "images":[img.image.name for img in Images.objects.filter(img_pro_id=pro.id)]
                      } for pro in Products.objects.all())
        return JsonResponse(prods, safe=False)
    

def magnage_pro(request):
    # if request.user is not None:
    if request.user.is_authenticated:
        if request.user.is_superuser:
            if request.method == 'POST':
                data = request.POST
                name =  data['title']
                desc = data['description']
                price = data['price']
                discount = data['discount']
                cat, created = Category.objects.get_or_create(sub_cat=data['sub_category'],main_cat=data['category'])
                avl_qty = data['avl_qty']
                prod = Products(prod_name=name,prod_dsc=desc,prod_price=price, prod_disc=discount,prod_avl_qty=avl_qty,pro_cat=cat)
                prod.save()
                id = prod.id
                for count,f in enumerate(request.FILES.getlist('file'),1):
                    ext = f.name.split('.')[-1]
                    f.name = f"prod_{id}_img{count}."+ext
                    img = Images(id=None,image=f,img_pro=prod)
                    img.save()
                return JsonResponse({"status":"Added Product Succesfully"},status=200 )
            return JsonResponse({"Err":"Invalid request method"},status=405)
        return JsonResponse({"Err":"Unautherized access"},status=401)
    return JsonResponse({"Err":"No User logged in"},status=400)


def manage_cart(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            data = json.loads(request.body)
            prod_id = int(data['product_id'])
            qty = int(data['quantity'])
            cart_item, created = Cart.objects.get_or_create(cart_product_id=prod_id,cart_customer=request.user, defaults={'ord_qty':qty})
            print(created)
            print(Products.objects.filter())
            if not created:
                cart_item.ord_qty = qty
                cart_item.save()
            return JsonResponse({"status":"Item added succesfully"})



def qmart(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            prod = Products.objects.get(pk=1)
            for f in request.FILES.getlist('file'):
                print(f)
                img = Images(id=None,image=f,img_pro=prod)
                img.save()
            img = Images(id=None, image=request.FILES['file'], img_pro=prod)
            img1 = Images(id=None,image=request.FILES['file1'])
            print(img1.image)
            img.save()
            print(request.POST['name'])
            return JsonResponse({"status":request.user.is_superuser})