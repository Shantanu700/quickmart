from django.db import IntegrityError
from django.db.models import F,Q
from django.http import JsonResponse
import json
import re
import magic
from django.conf import settings
from django.shortcuts import get_object_or_404
from qmart.models import *
from django.contrib.auth import authenticate, login, logout
import os


# Create your views here.


def register(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        first_name = data.get('Fname')
        if not first_name.isalpha():
            return JsonResponse({"Err":"Invalid First name, should be in alphabets"}, status=422)
        u_name = data.get('Uname')
        # if not u_name.isalnum():
        #     return JsonResponse({"Err":"Invalid User name, should be in alphabets or digits"}, status=422)
        l_name = data.get('Lname')
        # if not l_name.isalpha():
        #     return JsonResponse({"Err":"Invalid Last name, should be in alphabets"}, status=422)
        e_mail = data.get('Email')
        if not e_mail:
            return JsonResponse({"Err":"Email is required"},status=422)
        if not bool(re.match(r"[a-zA-Z0-9_\-\.]+[@][a-z]+[\.][a-z]{2,3}",e_mail)):
            return JsonResponse({"Err":"Invalid Email, should in the form abc@xyz.com"},status=422)
        mobile = data.get('Mobile')
        if not ((mobile.isnumeric() and len(mobile) == 10) or (not mobile)):
            return JsonResponse({"Err":"Invalid Phone, shoud be of 10 digits and numeric"},status=422)
        passwd_1 = data.get('Passwd1')
        passwd_2 = data.get('Passwd2')
        if not (passwd_1 and passwd_2):
            return JsonResponse({"Err":"Both passwords are required"},status=422)
        if not bool(re.match(r"^(?=.*[A-Z])(?=.*[!@#$&*])(?=.*[0-9])(?=.*[a-z]).{8,16}$",passwd_1)):
            return JsonResponse({"Err":"Weak Password, should include an upper case, a number, an special Symbol and should be of length between 8 to 16"},status=400)
        if all([first_name,e_mail,passwd_1,passwd_2]):
            if passwd_1 != passwd_2:
                return JsonResponse({"Err":"passwords do not match"}, status=409)
            if MyUser.objects.filter(email=e_mail).exists():
                return JsonResponse({"Err":"User already exists with this email"},status=409)
            new_user = MyUser.objects.create_user(u_name, e_mail, passwd_1,first_name=first_name,last_name = l_name,phone = mobile)
        # new_user.save()
            return JsonResponse({ 'f_name': first_name, 'e_mail': e_mail, 'l_name': l_name, },status=201)
        return JsonResponse({'Err':"First name, Email, Passwords are required"},status=422)
    return JsonResponse({"Err":"Invalid request method"},status=405) 

def signin(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        e_mail = data.get('Email')
        passwd = data.get('Passwd')
        if e_mail and passwd:
            if MyUser.objects.filter(email=e_mail).exists():
                User = authenticate(email=e_mail,password=passwd)
                if User is not None:
                    login(request,User)
                    return JsonResponse({"status":"Logged in Successfully", "is_admin": User.is_superuser},status=200 )
                return JsonResponse({"Err":"Password entered is incorrect"},status=400)
            return JsonResponse({"Err":"No user with these credentials"},status=400)
        return JsonResponse({'Err':'Email and Password are required'},status=422)
    return JsonResponse({"Err":"Invalid request method"},status=405)

def info(request):
    if request.method == 'GET':
        data = {"Category": {cat['main_cat'] : [sub_cat['sub_cat'] for sub_cat in Category.objects.filter(main_cat=cat['main_cat']).values('sub_cat')] for cat in Category.objects.values('main_cat').distinct()}}
        data['is_authenticated'] = request.user.is_authenticated
        if request.user.is_authenticated:
            data['first_name'] = request.user.first_name
            data["is_admin"] = request.user.is_superuser
            return JsonResponse(data)
        return JsonResponse(data)
    return JsonResponse({"Err":"Invalid request method"},status=405)
            

def signout(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            logout(request)
            return JsonResponse({"status":"Logged out Successfully"},status=200 )
        return JsonResponse({"Err":"No any User was autherized"},status=400)
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
                      "thumbnail":Images.objects.get(image__startswith=f'product_{pro.id}/prod_{pro.id}_img1').image.name,
                      "images":[img.image.name for img in Images.objects.filter(img_pro_id=pro.id).exclude(image__startswith=f'product_{pro.id}/prod_{pro.id}_img1')]
                      } for pro in Products.objects.filter(is_deleted=False))
        return JsonResponse(prods, safe=False)
    return JsonResponse({"Err":"Invalid request method"},status=405)
    
    

def manage_pro(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            if request.user.is_superuser:
                if request.FILES.getlist('file'):
                    images_list = request.FILES.getlist('file')
                    if len(images_list) > 8:
                        return JsonResponse({'Err':"You can't upload more than 8 images"}, status=422)
                    for count,f in enumerate(images_list,1):
                        print(f)
                        ext = f.name.split('.')[-1]
                        print(ext)
                        content_type = f.content_type
                        mime_type = magic.from_buffer(f.read(1024), mime=True)
                        size = f.size
                        if size > settings.MAX_IMG_SIZE:
                            return JsonResponse({'Err':f'size {size} larger than 1 MB'},status=422)
                        if content_type not in settings.ALLOWED_IMG_TYPES.values():
                            return JsonResponse({'Err':'invalid image content-type'},status=422)
                        if ext not in settings.ALLOWED_IMG_TYPES.keys():
                            return JsonResponse({'Err':'invalid image extension'},status=422)
                        if mime_type not in settings.ALLOWED_IMG_TYPES.values() and mime_type != content_type:
                            return JsonResponse({'Err':'invalid image mime-type'},status=422)
                    data = request.POST
                    # print(data)
                    name =  data.get('title')
                    # print(type(name))
                    desc = data.get('description')
                    # print(type(desc))
                    price = data.get('price')
                    # print(type(price))
                    discount = data.get('discount')
                    if discount:
                        if int(discount) > 95:
                            return JsonResponse({"Err":"Invalid Discount"},status=422)
                    sub_category = data.get('sub_category')
                    # print(type(sub_category))
                    main_category = data.get('category')
                    # print(type(main_category))
                    avl_qty = data.get('avl_qty')
                    if all([name,desc,price,sub_category,main_category,avl_qty]):
                        cat, created = Category.objects.get_or_create(sub_cat=sub_category,main_cat=main_category)
                        print(cat)
                        prod = Products(prod_name=name,prod_dsc=desc,prod_price=price, prod_disc=discount,prod_avl_qty=avl_qty,pro_cat=cat)
                        prod.save()
                    else:
                        return JsonResponse({'Err':'Title, discription, price, sub-category,main-category, available quantity are required'},status=422)
                    id = prod.id
                    for count,f in enumerate(images_list,1):
                        # print(f)
                        # ext = f.name.split('.')[-1]
                        # print(ext)
                        # content_type = f.content_type
                        # mime_type = magic.from_buffer(f.read(1024), mime=True)
                        # size = f.size
                        # if size > settings.MAX_IMG_SIZE:
                        #     return JsonResponse({'Err':f'size {size} larger than 1 MB'},status=422)
                        # if content_type not in settings.ALLOWED_IMG_TYPES.values():
                        #     return JsonResponse({'Err':'invalid image content-type'},status=422)
                        # if ext not in settings.ALLOWED_IMG_TYPES.keys():
                        #     return JsonResponse({'Err':'invalid image extension'},status=422)
                        # if mime_type not in settings.ALLOWED_IMG_TYPES.values() and mime_type != content_type:
                        #     return JsonResponse({'Err':'invalid image mime-type'},status=422)
                        f.name = f"prod_{id}_img{count}."+ext
                        img = Images(id=None,image=f,img_pro=prod)
                        img.save()
                    return JsonResponse({"status":"Added Product Succesfully"},status=200)
                return JsonResponse({"Err":"Images were not recieved"},status=422)
            return JsonResponse({"Err":"Unautherized access"},status=401)
        return JsonResponse({"Err":"No User logged in"},status=400)
    if request.method == 'PUT':
        if request.user.is_authenticated:
            if request.user.is_superuser:
                data = json.loads(request.body)
                prod_id = data.get('id')
                if not prod_id:
                    return JsonResponse({"Err":"Product ID is required"},status=422)
                name =  data.get('title')
                desc = data.get('description')
                price = data.get('price')
                discount = data.get('discount')
                if discount:
                    if discount > 95:
                        return JsonResponse({"Err":"Invalid Discount"},status=422)
                avl_qty = data.get('avl_qty')
                sub_category = data.get('sub_category')
                main_category = data.get('category')
                product = Products.objects.filter(id=prod_id)
                # cat_id = Category.objects.get(sub_cat=sub_category,main_cat=main_category).id
                if name:
                    product.update(prod_name=name)
                if desc:
                    product.update(prod_dsc=desc)
                if price:
                    product.update(prod_price=price)
                if discount is not None:
                    product.update(prod_disc=discount)
                if avl_qty:
                    product.update(prod_avl_qty=avl_qty)
                if sub_category and main_category:
                    cat_id = get_object_or_404(Category, sub_cat=sub_category, main_cat=main_category).id
                    product.update(pro_cat_id=cat_id)
                return JsonResponse({"status":"Updated"})
            return JsonResponse({"Err":"Unautherized access"},status=401)
        return JsonResponse({"Err":"No User logged in"},status=400)

    if request.method == 'DELETE':
        if request.user.is_authenticated:
            if request.user.is_superuser:
                data = json.loads(request.body)
                del_id = data.get('id')
                if del_id:
                    del_prod = Products.objects.filter(id=del_id).update(is_deleted=True)
                    return JsonResponse({"status":f"product number {del_id} deleted successfully"})
            return JsonResponse({"Err":"Unautherized access"},status=401)
        return JsonResponse({"Err":"No User logged in"},status=400)
    # if request.method == 'PATCH':
    #     data = json.loads(request.body)
    #     print(data)
    #     return JsonResponse({'status':'patch request accepted'}
    return JsonResponse({"Err":"Invalid request method"},status=405)

def update_images(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            if request.user.is_superuser:
                prod_id = request.GET.get('id')
                img_list = Images.objects.filter(img_pro__id=prod_id).values('id','image',title=F('img_pro__prod_name'),pro_id=F('img_pro__id'))
                return JsonResponse(list(img_list),safe=False)
            return JsonResponse({"Err":"Unautherized access"},status=401)
        return JsonResponse({"Err":"No User logged in"},status=400)
    if request.method == 'POST':
        if request.user.is_authenticated:
            if request.user.is_superuser:
                data = request.POST
                print(data)
                del_id_list = request.POST.get('img')
                prod_id = int(request.POST.get('id'))
                # print(prod_id)
                print(del_id_list)
                # print(type(del_id_list.split(',')))
                # print(del_id_list.split(','))
                if del_id_list:
                    num_del_images = del_id_list.count(',')+1
                else:
                    num_del_images = 0
                images_list = request.FILES.getlist('file')
                num_added_images = len(images_list)
                if (num_added_images-num_del_images >= 8):
                    return JsonResponse({"Err":"You can't enter more than 8 images"},status=422)
                # f = request.FILES.get('file')
                # print(images_list)
                if images_list:
                    for f in images_list:
                        ext = f.name.split('.')[-1]
                        content_type = f.content_type
                        mime_type = magic.from_buffer(f.read(1024), mime=True)
                        size = f.size
                        if size > settings.MAX_IMG_SIZE:
                            return JsonResponse({'Err':f'size {size} larger than 1 MB'},status=422)
                        if content_type not in settings.ALLOWED_IMG_TYPES.values():
                            return JsonResponse({'Err':'invalid image content-type'},status=422)
                        if ext not in settings.ALLOWED_IMG_TYPES.keys():
                            return JsonResponse({'Err':'invalid image extension'},status=422)
                        if mime_type not in settings.ALLOWED_IMG_TYPES.values() and mime_type != content_type:
                            return JsonResponse({'Err':'invalid image mime-type'},status=422)
                        
                        if del_id_list:
                            # print(del_id_list)
                            del_id_list = del_id_list.split(',')
                            
                            img = Images.objects.get(image=del_id_list.pop())
                            img_name = img.image.name.split('/')[-1]
                            print(img_name)
                            # print(del_id_list)
                            img.image.delete(save=False)
                            img.image.save(img_name,f)
                            # print(images_list)
                            images_list.remove(f)
                if del_id_list:
                    if type(del_id_list) == str:                        
                        del_id_list = del_id_list.split(',')
                    for del_id in del_id_list:
                        img = Images.objects.get(image=del_id)
                        if os.path.exists('Media'+img.image.name):
                            os.remove('Media'+img.image.name)
                        img.delete()
                if images_list:
                    last_img = Images.objects.filter(img_pro__id=prod_id).latest('id').image.name
                    last_img_number = int(last_img[-5]) + 1
                    # print(f.name)
                    # print(images_list)

                    for count, f in enumerate(images_list,last_img_number):
                        # print('ho')
                        ext = f.name.split('.')[-1]
                        content_type = f.content_type
                        mime_type = magic.from_buffer(f.read(1024), mime=True)
                        size = f.size
                        if size > settings.MAX_IMG_SIZE:
                            return JsonResponse({'Err':f'size {size} larger than 1 MB'},status=422)
                        if content_type not in settings.ALLOWED_IMG_TYPES.values():
                            return JsonResponse({'Err':'invalid image content-type'},status=422)
                        if ext not in settings.ALLOWED_IMG_TYPES.keys():
                            return JsonResponse({'Err':'invalid image extension'},status=422)
                        # if mime_type not in settings.ALLOWED_IMG_TYPES.values() and mime_type != content_type:
                        #     print(mime_type)
                        #     return JsonResponse({'Err':'invalid image mime-type'},status=422)
                        f.name = f"prod_{prod_id}_img{count}."+ext
                        print(f.name)
                        img = Images(id=None,image=f,img_pro_id=prod_id)
                        img.save()
                        # print(img.image.name)
                    # f.name = f"prod_{prod_id}_img{last_img_number}"+ext
                    # print(images_list)
                    # if del_id_list:
                    #     print(del_id_list)
                    #     img = Images.objects.get(id=int(del_id_list.pop()))
                        # img.delete()
                        # img.save()
                            # print(img.image.name)
                            # print(img.image)
                            # print(img.image.name)
                            # print(del_id_list)
                #     print(f.name)
                    # images_list[count-1].image.delete(save=False)
                    # # print(prod_image.image.name)
                    # images_list[count-1].image.save(f.name,f)
                    # if os.path.exists(''):
                    #     pass
                    # prod_list.update(image=f)
                #     print(file)
                # print(prod_list)
                return JsonResponse({'status':f'recieved id 5'})
            return JsonResponse({"Err":"Unautherized access"},status=401)
        return JsonResponse({"Err":"No User logged in"},status=400)
    return JsonResponse({"Err":"Invalid request method"},status=405)






def manage_cart(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            data = list(Cart.objects.filter(cart_customer=request.user).values(product=F('cart_product'),qt=F('ord_qty')))
            return JsonResponse(data,status=200,safe=False)
        return JsonResponse({"Err":"No User logged in"},status=400)
            # pass
    
    elif request.method == 'POST':
        if request.user.is_authenticated:
            data = json.loads(request.body)
            for item in data:
                prod_id = item.get('product')
                qty = item.get('qt')
                if not (prod_id and qty):
                    return JsonResponse({'Err':'Product ID and Quantity are required'},status=422)
                cart_item, created = Cart.objects.get_or_create(cart_product_id=prod_id,cart_customer=request.user, defaults={'ord_qty':qty})
                # print(Products.objects.filter())
                if not created:
                    cart_item.ord_qty = qty
                    cart_item.save()
            return JsonResponse({"status":"Items added succesfully"})
        return JsonResponse({"Err":"No User logged in"},status=400)
    elif request.method == 'PUT':
        if request.user.is_authenticated:
            data = json.loads(request.body)
            Cart.objects.filter(cart_customer=request.user).delete()
            for item in data:
                prod_id = item.get('product')
                qty = item.get('qt')
                if not (prod_id and qty):
                    return JsonResponse({'Err':'Product ID and Quantity are required'},status=422)
                cart_item = Cart.objects.create(cart_product_id=prod_id,cart_customer=request.user, ord_qty=qty)
            return JsonResponse({"status":"Updated Cart Succesfully"},status=200)
        return JsonResponse({"Err":"No User logged in"},status=400)
    # elif request.method == 'DELETE':
    #     prod_id = request.GET.get('product_id')
    #     print(prod_id)
    #     obj = get_object_or_404(Cart, cart_product_id=prod_id)
    #     obj.delete()
    #     return JsonResponse({"status":"Item deleted succesfully"})
    return JsonResponse({"Err":"Invalid request method"},status=405)

def orders(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            data = json.loads(request.body)
            # print(data)
            prods = data.get('product')
            customer_addr = data.get('address')
            mop = data.get('mode')
            c_code = data.get('coupon_code')
            if not all([prods, customer_addr, mop]):
                return JsonResponse({'Err':'Products, customer, Mode of Payment are required'},status=422)
            last_order_id = Orders.objects.latest('ord_id').ord_id
            current_order_id = last_order_id + 1
            print(current_order_id)
            for prod in prods:
                prod_id = prod.get('id')
                prod_qt = prod.get('qty')
                if not (prod_id and prod_qt):
                    return JsonResponse({'Err':'Product ID and quantity are required'},status=422)
                product = Products.objects.get(id=prod_id)
                if product.prod_avl_qty < prod_qt:
                    return JsonResponse({"Err":"Out of Stock"},status=400)
                product.prod_avl_qty = F('prod_avl_qty') - prod_qt
                product.save()
                order = Orders.objects.create(product_id=prod_id,customer=request.user,ship_addr=customer_addr,ord_qty=prod_qt,mode_of_payment=mop,ord_id=current_order_id)
                # order.ord_id = last_order_id.ord_id + 1
                # order.save
            # qty = data['qt']
            # ord_status = data['status']
            if c_code:
                if not used_coupons.objects.filter(coupon__code=c_code,cstmr_id=request.user).exists() and Coupons.objects.get(code=c_code).count:
                    # print("code applied")
                    coupon = Coupons.objects.get(code=c_code)
                    coupon.count = F("count") - 1
                    coupon.save()
                    usd_code = used_coupons.objects.create(coupon=coupon,cstmr_id=request.user)
                    order.coupon_used = coupon
                    order.save()
            else:
                print("code not applied")
            return JsonResponse({'status':'Order palced succesfully'})
        return JsonResponse({"Err":"No User logged in"},status=400)
    if request.method == 'GET':
        if request.user.is_authenticated:
            if request.user.is_superuser:
                orders = [{"title":order.product.prod_name,
                        "id":order.id,
                       "price":order.product.prod_price,
                       "qty":order.ord_qty,
                       "status":order.get_status_display(),
                       "status_code":order.status,
                       "discount":order.product.prod_disc,
                       "thumbnail":Images.objects.get(image__startswith=f'product_{order.product.id}/prod_{order.product.id}_img1').image.name} for order in Orders.objects.all()]
                return JsonResponse(list(reversed(orders)),safe=False)    
            # orders = Orders.objects.filter(customer=request.user).values(title=F('product__prod_name'),price=F('product__prod_price'),qty=F('ord_qty'),id=F('product__id'))
            # images = Images.objects.filter(image__startswith=f'product_{orders[0][id]}/prod_{orders[0][id]}_img1').values()
            orders = [{"title":order.product.prod_name,
                       "price":order.product.prod_price,
                       "qty":order.ord_qty,
                       "status":order.get_status_display(),
                       "discount":order.product.prod_disc,
                       "thumbnail":Images.objects.get(image__startswith=f'product_{order.product.id}/prod_{order.product.id}_img1').image.name} for order in Orders.objects.filter(customer=request.user)]
            return JsonResponse(list(orders),safe=False)
        return JsonResponse({"Err":"No User logged in"},status=400)

    if request.method == 'PUT':
        if request.user.is_authenticated:
            if request.user.is_superuser:
                data = json.loads(request.body)
                status_ = data.get('status')
                ord_id = data.get('id')
                if status_:
                    order_to_update = Orders.objects.get(id=ord_id)
                    order_to_update.status = list(Orders.choices_of_status.keys())[list(Orders.choices_of_status.values()).index(status_)]
                    order_to_update.save()
                    return JsonResponse({"status":"Updated Successfully"})
                return JsonResponse({"Err":"No status Found"},status=404)
            return JsonResponse({"Err":"Unautherized access"},status=401)
        return JsonResponse({"Err":"No User logged in"},status=400)
    return JsonResponse({"Err":"Invalid request method"},status=405)
    
def manage_coupons(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.user.is_superuser:
                data = json.loads(request.body)
                c_code = data.get('code')
                c_count = data.get('count')
                c_disc = data.get('discount')
                if all([c_code,c_count,c_disc]):
                    if Coupons.objects.filter(code=c_code).exists():
                        return JsonResponse({"Err":"Coupon already exist"})
                    coupon = Coupons.objects.create(code=c_code,count=c_count,discount=c_disc)
                else:
                    return JsonResponse({"Err":"Code, count, discount are required"},status=422)
                return JsonResponse({"status":"Added Coupon"})
            return JsonResponse({"Err":"Unautherized access"},status=401)
        return JsonResponse({"Err":"No User logged in"},status=400)
    elif request.method == 'GET':
        if request.user.is_authenticated:
            c_code = request.GET.get('coupon')
            if not c_code:
                return JsonResponse({'Err':'No any coupon code'},status=404)
            if used_coupons.objects.filter(coupon__code=c_code,cstmr_id=request.user).exists():
                return JsonResponse({'Err':'coupon already used'},status=409)
            if Coupons.objects.filter(code=c_code).exists() and Coupons.objects.get(code=c_code).count:
                discount = Coupons.objects.get(code=c_code).discount
                return JsonResponse({'discount':discount})
            return JsonResponse({"Err":'Invalid coupon'},status=404)
            #     return JsonResponse({'recieved':"coupon"})
            # else:
            #     return JsonResponse({'not recieved':"coupon"})



def test(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            # prod = Products.objects.all().values()
            file = request.FILES.get('file')
            if file:
                content_type = file.content_type
                mime_type = magic.from_buffer(file.read(1024), mime=True)
                size = file.size
                ext = file.name.split('.')[-1]
                # print(ext,size)
            else:
                print('NO IMAGE FOUND')
                # if size <= settings.MAX_IMG_SIZE and content_type in settings.ALLOWED_IMG_TYPES.keys() and 
            # for f in request.FILES.getlist('file'):
            #     print(f)
            #     img = Images(id=None,image=f,img_pro=prod)
            #     img.save()
            # img = Images(id=None, image=request.FILES['file'], img_pro=prod)
            # img1 = Images(id=None,image=request.FILES['file1'])
            # print(img1.image)
            # img.save()
            # print(request.POST['name'])
            return JsonResponse({"test":"This api is for testing"}, safe=False)