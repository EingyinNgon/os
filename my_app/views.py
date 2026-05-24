from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Category, UserProfile, SubCategory, Item, Cart, CartItem, Order
from django.core.paginator import Paginator

def is_admin(user):
    return user.is_superuser

# @login_required(login_url='login')
def index(request):
    sub_categories = SubCategory.objects.all().distinct()
    
    # ၂။ User က Dropdown ကနေ ရွေးလိုက်တဲ့ SubCategory ID ကို URL ကနေ လှမ်းဖမ်းမယ်
    selected_sub_cat = request.GET.get('subcategory')
    
    if selected_sub_cat and selected_sub_cat != 'all' and selected_sub_cat != '':
        items = Item.objects.filter(
            sub_category_id=selected_sub_cat, 
            is_deleted=False
        )
    else:
        items = Item.objects.filter(is_deleted=False)
    # ၄။ HTML ဘက်ကို ဒေတာတွေ ပို့ရန်
    context = {
        'sub_categories': sub_categories,
        'items': items,
        'selected_sub_cat': str(selected_sub_cat) if selected_sub_cat else 'all'
    }
    
    return render(request, 'index.html', context)

@login_required(login_url='login')
def user_list(request):
    # print(request.user.is_superuser)
    if request.user.is_superuser:
        users = User.objects.all().select_related('userprofile').order_by('-date_joined')
        paginator = Paginator(users, 10)

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, 'user/user_list.html', {'users': page_obj})
    else:
        return HttpResponse('invalid route')
    
@login_required
@user_passes_test(is_admin)
def add_user(request):
    # print(request.user.is_superuser)
    if request.method == "POST":
        # ၁။ User Table အတွက် Data ယူမယ်
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Password နှစ်ခု မတူညီပါဘူး။ ပြန်စစ်ပေးပါ။")
            return render(request, 'user/add_user.html')
        
        # ၂။ UserProfile Table အတွက် Data ယူမယ်
        # phone = request.POST.get('phone_no')
        # address = request.POST.get('address')
        # vantor = request.POST.get('vantor')
        
        try: 
            user = User.objects.create_user(username=username, password=password, email=email)
            messages.success(request, f"User {username} ကို အောင်မြင်စွာ ဆောက်ပြီးပါပြီ။")
            # Signal က ဆောက်ပေးလိုက်တဲ့ Profile ကိုပဲ ပြန်ယူပြီး အချက်အလက်ဖြည့်မယ်
            profile = user.userprofile  
            profile.phone_no = request.POST.get('phone_no')
            print( request.POST.get('phone_no'))
            profile.address = request.POST.get('address')

            # ✨ HTML Text အကွက်ကနေ ဆိုင်နာမည်ကို လှမ်းယူမယ်
            shop_name = request.POST.get('vantor') 
            logo = request.FILES.get('vendor_image') # ပုံကိုဖမ်းမယ်

            if shop_name: # တကယ်လို့ ဆိုင်နာမည် ရိုက်ထည့်ထားခဲ့ရင်...
                profile.vantor = shop_name       # သင့် Model ထဲက CharField ထဲ ဆိုင်နာမည်သိမ်းမယ်
                profile.is_vendor = True         # သူက Vendor ဖြစ်သွားပြီမို့ True ပေးမယ်
                if logo:
                 profile.shop_logo = logo     # ဆိုင် Logo ပုံပါရှိရင် တစ်ခါတည်း သိမ်းမယ်
            else:
                profile.is_vendor = False        # ဆိုင်နာမည် မရိုက်ရင် ရိုးရိုး user အဖြစ် False ပဲ ထားမယ်            
            profile.save()          
                    
            return redirect('user_list')
        except Exception as e:
            messages.error(request, f"Error: {e}")
        
    return render(request, 'user/add_user.html')

@login_required
@user_passes_test(is_admin)
def user_detail(request, pk):
    # ID နဲ့ ရှာမယ်၊ မရှိရင် 404 Error ပေးမယ်
    user_obj = get_object_or_404(User, pk=pk)
    return render(request, 'user/user_detail.html', {'user_obj': user_obj})

@login_required
@user_passes_test(is_admin)
def update_user(request, pk):
    # ပြင်မယ့် User ကို ရှာမယ်
    user_obj = get_object_or_404(User, pk=pk)
    
    if request.method == "POST":
        # Form ကလာတဲ့ data အသစ်တွေကို ယူမယ်
        user_obj.username = request.POST.get('username')
        user_obj.email = request.POST.get('email')
        
        # Profile data တွေကို ယူပြီး ပြင်မယ်
        profile = user_obj.userprofile
        profile.phone_no = request.POST.get('phone_no')
        profile.vantor = request.POST.get('vantor')
        profile.address = request.POST.get('address')
        
        # Database ထဲ သိမ်းမယ်
        user_obj.save()
        profile.save()
        
        return redirect('user_list')

    return render(request, 'user/update_user.html', {'user_obj': user_obj})

# User ဖျက်ရန် (Delete)
@login_required
@user_passes_test(is_admin)
def delete_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.delete()
    return redirect('user_list')

@login_required
@user_passes_test(is_admin)
def add_category(request):
    if request.method == "POST":
        c_name = request.POST.get('name')
        c_desc = request.POST.get('descriptions')
        
        # Category ကို database ထဲ ထည့်မယ်
        Category.objects.create(
            name=c_name,
            descriptions=c_desc,
            created_by=request.user # လက်ရှိ login ဝင်ထားတဲ့ admin ကို ထည့်ပေးတာ
        )
        return redirect('category_list')
    
    return render(request, 'category/add_category.html')

@login_required
@user_passes_test(is_admin)   
def category_list(request):
   # ဖျက်မထားတဲ့ Category တွေကိုပဲ ယူမယ်
    categories = Category.objects.filter(is_deleted=False).order_by('-created_at')
    paginator = Paginator(categories, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'category/category_list.html', {'categories': page_obj})

@login_required
@user_passes_test(is_admin)
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.is_deleted = True  # အပြီးမဖျက်ဘဲ ဖျက်ထားတယ်လို့ပဲ မှတ်လိုက်တာ
    category.save()
    return redirect('category_list')

@login_required
@user_passes_test(is_admin)
def edit_category(request, pk):
    # ပြင်မယ့် Category ကို ID (pk) နဲ့ ရှာမယ်၊ မရှိရင် 404 error ပြမယ်
    category = get_object_or_404(Category, pk=pk)

    if request.method == "POST":
        # Form ထဲက အချက်အလက်သစ်တွေကို ယူမယ်
        category.name = request.POST.get('name')
        category.descriptions = request.POST.get('descriptions')
        
        # Database ထဲမှာ သိမ်းမယ်
        category.save()
        
        # ပြီးရင် category list စာမျက်နှာဆီ ပြန်ပို့မယ်
        return redirect('category_list')

    # GET method ဆိုရင် လက်ရှိ data တွေနဲ့ edit_category.html ကို ပြမယ်
    return render(request, 'category/edit_category.html', {'category': category})

def register_user(request):
    if request.method == "POST":
        u_name = request.POST.get('username')
        u_pass = request.POST.get('password')
        u_email = request.POST.get('email')
        p_phone = request.POST.get('phone_no')
        p_address = request.POST.get('address')

        # ၁။ User ကို အရင်ဆောက်တယ်
        new_user = User.objects.create_user(username=u_name, password=u_pass, email=u_email)

        # ၂။ အပေါ်က Signal ကြောင့် Profile က အလိုအလျောက် ဆောက်ပြီးသား ဖြစ်နေမှာမို့လို့ 
        # ကျန်တဲ့ data တွေကို update လုပ်ပေးလိုက်ရုံပါပဲ
        profile = new_user.userprofile
        profile.phone_no = p_phone
        profile.address = p_address
        profile.save()

        return redirect('login')
    
    return render(request, 'register.html')

@login_required
@user_passes_test(is_admin)
def add_subcategory(request):
    if request.method == "POST":
        category_id = request.POST.get('category')
        name = request.POST.get('name')
        desc = request.POST.get('descriptions')
        
        category = get_object_or_404(Category, id=category_id)
        
        SubCategory.objects.create(
            category=category,
            name=name,
            descriptions=desc,
            created_by=request.user
        )
        return redirect('subcategory_list')

    # Dropdown မှာ ပြဖို့အတွက် Category တွေကို ယူသွားမယ်
    categories = Category.objects.filter(is_deleted=False)
    return render(request, 'subcategory/add_subcategory.html', {'categories': categories})

@login_required
@user_passes_test(is_admin)
def subcategory_list(request):
    subcategories = SubCategory.objects.filter(is_deleted=False).order_by('-created_at')
    paginator = Paginator(subcategories, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'subcategory/subcategory_list.html', {'subcategories':  page_obj})

@login_required
@user_passes_test(is_admin)
def delete_subcategory(request, pk):
    sub = get_object_or_404(SubCategory, pk=pk)
    sub.is_deleted = True
    sub.save()
    return redirect('subcategory_list')

@login_required
@user_passes_test(is_admin)
def edit_subcategory(request, pk):
    sub = get_object_or_404(SubCategory, pk=pk)
    if request.method == "POST":
        category_id = request.POST.get('category')
        sub.category = get_object_or_404(Category, id=category_id)
        sub.name = request.POST.get('name')
        sub.descriptions = request.POST.get('descriptions')
        sub.save()
        return redirect('subcategory_list')
    
    categories = Category.objects.filter(is_deleted=False)
    return render(request, 'subcategory/edit_subcategory.html', {
        'subcategory': sub, 
        'categories': categories
    })

@login_required
def item_list(request):
    # ၁။ အရင်ဆုံး User Role အလိုက် သက်ဆိုင်ရာ ပစ္စည်းများကို ဆွဲထုတ်မည်
    if request.user.is_superuser:
        # Admin ဆိုရင် မဖျက်ရသေးတဲ့ Item အားလုံးကို ပြမယ်
        items = Item.objects.filter(is_deleted=False).select_related('sub_category', 'created_by')
    elif hasattr(request.user, 'userprofile') and request.user.userprofile.is_vendor:
        # Vendor ဆိုရင် သူကိုယ်တိုင် ဆောက်ထားတဲ့ ပစ္စည်းတွေကိုပဲ ပြမယ်
        items = Item.objects.filter(created_by=request.user, is_deleted=False).select_related('sub_category')
    else:
        items = Item.objects.none()
        
    # ၂။ 🌟 [ဤနေရာသို့ ရွှေ့လိုက်ပါပြီ] ၎င်းပစ္စည်းများကိုမှ Paginator ဖြင့် စာမျက်နှာခွဲမည်
    paginator = Paginator(items, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
        
    # ၃။ HTML ထဲတွင် items ရော page_obj ပါ အဆင်ပြေပြေ သုံးနိုင်အောင် Context တွင် နှစ်ခုလုံး ထည့်ပေးလိုက်ပါသည်
    context = {
        'items': page_obj,    # loop ပတ်ရန်အတွက်
        'page_obj': page_obj  # pagination ခလုတ်များ (Next/Prev) လုပ်ရန်အတွက်
    }
    
    return render(request, 'item/item_list.html', context)

# ၂။ Add Item (Create)
@login_required
def add_item(request):
    # Admin သို့မဟုတ် Vendor ဖြစ်မှ ပစ္စည်းတင်ခွင့်ပေးမယ်
    if not (request.user.is_superuser or request.user.userprofile.is_vendor):
        messages.error(request, "You are not allowed to post items!")
        return redirect('user_list')

    if request.method == "POST":
        name = request.POST.get('name')
        sub_cat_id = request.POST.get('sub_category')
        amount = request.POST.get('amount')
        size = request.POST.get('size')
        buy_price = request.POST.get('buy_price')
        sale_price = request.POST.get('sale_price')
        product_image = request.FILES.get('item_image')
        
        # Discount logic (တကယ်လို့ Form က ပါလာရင်)
        is_discount = request.POST.get('is_discount') == 'on'
        discount = request.POST.get('discount') or 0.00

        try:
            Item.objects.create(
                name=name,
                sub_category_id=sub_cat_id,
                amount=amount,
                size=size,
                buy_price=buy_price,
                sale_price=sale_price,
                image=product_image,
                is_discount=is_discount,
                discount=discount,
                created_by=request.user  # ဘယ်သူဆောက်တာလဲဆိုတဲ့နေရာမှာ လက်ရှိ login ဝင်ထားတဲ့ user ကို ထည့်မယ်
            )
            messages.success(request, f"Product {name} ကို အောင်မြင်စွာ တင်ပြီးပါပြီ။")
            return redirect('item_list')
        except Exception as e:
            messages.error(request, f"Error: {e}")

    # Dropdown မှာ ရွေးဖို့အတွက် SubCategory တွေကို ဆွဲထုတ်ပေးမယ်
    sub_categories = SubCategory.objects.all()
    return render(request, 'item/add_item.html', {'sub_categories': sub_categories})

@login_required
def edit_item(request, item_id):
    # ပြင်မယ့် Item ကို Database ထဲက လှမ်းရှာမယ်
    item = get_object_or_404(Item, id=item_id, is_deleted=False)
    
    # Security: မိမိပစ္စည်း မဟုတ်ရင် (Admin လည်းမဟုတ်ရင်) ပေးမပြင်ဘူး
    if not (request.user.is_superuser or item.created_by == request.user):
        messages.error(request, "သင်က ဒီပစ္စည်းကို ပြင်ဆင်ပိုင်ခွင့် မရှိပါဘူး။")
        return redirect('item_list')

    if request.method == "POST":
        item.name = request.POST.get('name')
        item.sub_category_id = request.POST.get('sub_category')
        item.amount = request.POST.get('amount')
        item.buy_price = request.POST.get('buy_price')
        item.sale_price = request.POST.get('sale_price')
        
        # ပုံအသစ် တင်လာရင် အဟောင်းနေရာမှာ အစားထိုးမယ်
        new_image = request.FILES.get('item_image')
        if new_image:
            item.image = new_image
            
        item.save()
        messages.success(request, f"Product {item.name} ကို ပြင်ဆင်ပြီးပါပြီ။")
        return redirect('item_list')

    sub_categories = SubCategory.objects.all()
    return render(request, 'item/edit_item.html', {'item': item, 'sub_categories': sub_categories})


# ၄။ Delete Item (Delete)
@login_required
def delete_item(request, item_id):
    item = get_object_or_404(Item, id=item_id, is_deleted=False)
    
    # Security စစ်ဆေးခြင်း
    if not (request.user.is_superuser or item.created_by == request.user):
        messages.error(request, "သင်က ဒီပစ္စည်းကို ဖျက်ပိုင်ခွင့် မရှိပါဘူး။")
        return redirect('item_list')

    # သင့် Model ရဲ့ Plan အတိုင်း Database ထဲက အပြီးမဖျက်ဘဲ Status ကိုပဲ True ပေးလိုက်တာပါ (Soft Delete)
    item.is_deleted = True
    item.save()
    
    messages.success(request, f"Product {item.name} ကို ဖျက်သိမ်းပြီးပါပြီ။")
    return redirect('item_list')

# 1. Add to Cart Function (ခြင်းတောင်းထဲ ပစ္စည်းထည့်ခြင်း)
@login_required
def add_to_cart(request, item_id):
    item = get_object_or_404(Item, id=item_id, is_deleted=False)
    
    # လက်ရှိ User မှာ Cart မရှိသေးရင် Auto ဆောက်ခိုင်းမယ် (get_or_create)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # ဒီပစ္စည်းက ခြင်းတောင်းထဲမှာ ရှိပြီးသားလား စစ်မယ်
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, item=item)
    
    if not item_created:
        # ရှိပြီးသားဆိုရင် အရေအတွက်ကို ၁ တိုးမယ်
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, f"{item.name} ရဲ့ အရေအတွက်ကို တိုးမြှင့်လိုက်ပါပြီ။")
    else:
        messages.success(request, f"{item.name} ကို ခြင်းတောင်းထဲ ထည့်လိုက်ပါပြီ။")

    total_count = CartItem.objects.filter(cart=cart).count()
    request.session['cart_items_count'] = total_count

    next_url = request.GET.get('next', 'index')
    return redirect(next_url)

# 2. Cart Detail View (ခြင်းတောင်းထဲက ပစ္စည်းများ သွားကြည့်ရန် Page)
@login_required
def cart_detail(request):
    # User ရဲ့ cart ကို ဆွဲထုတ်မယ်၊ မရှိသေးရင် အလွတ်တစ်ခု ဆောက်ပေးမယ်
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items_list = CartItem.objects.filter(cart=cart)

    paginator = Paginator(cart_items_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'cart': cart,
        'cart_items': page_obj, 
    }
    return render(request, 'cart_detail.html', context)



@login_required
def update_cart_quantity(request, item_id, action):
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = CartItem.objects.filter(cart=cart, item_id=item_id).first()
    
    if cart_item:
        if action == 'increase':
            if cart_item.item.amount > cart_item.quantity:
                cart_item.quantity += 1
                cart_item.save()
        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
                
    # ခြင်းတောင်းထဲက ပစ္စည်းအရေအတွက် Session ကို Update ပြန်လုပ်ခြင်း
    from django.db import models
    total_items = CartItem.objects.filter(cart=cart).aggregate(total=models.Sum('quantity'))['total'] or 0
    request.session['cart_items_count'] = total_items
    
    return redirect('cart_detail')

@login_required
def checkout_view(request):
    """ ဝယ်သူကို လိပ်စာ၊ ဖုန်းနံပါတ် ဖြည့်ခိုင်းပြီး Order Summary ပြသမည့် စာမျက်နှာ """
    cart = Cart.objects.filter(user=request.user).first()
    
    if not cart or not CartItem.objects.filter(cart=cart).exists():
        return redirect('cart_detail')
        
    cart_items = CartItem.objects.filter(cart=cart)
    total_amount = sum(cart_item.item.sale_price * cart_item.quantity for cart_item in cart_items)
    
    # UserProfile ထဲက ရှိပြီးသား ဖုန်းနှင့် လိပ်စာကို ဆွဲထုတ်ပြီး Form မှာ ကြိုပြထားရန်
    profile = UserProfile.objects.filter(user=request.user).first()
    
    context = {
        'cart_items': cart_items,
        'total_amount': total_amount,
        'profile': profile,
    }
    return render(request, 'checkout.html', context)


@login_required
def place_order(request):
    """ Checkout Form က အချက်အလက်များကို ယူပြီး Database ထဲသို့ Order တကယ်သိမ်းမည့်နေရာ """
    if request.method == 'POST':
        cart = Cart.objects.filter(user=request.user).first()
        if not cart or not CartItem.objects.filter(cart=cart).exists():
            return redirect('cart_detail')
            
        cart_items = CartItem.objects.filter(cart=cart)
        
        shipping_phone = request.POST.get('phone_no')
        shipping_address = request.POST.get('address')
        
        # ခြင်းတောင်းထဲက ပစ္စည်းတစ်ခုချင်းစီအတွက် မင်းရဲ့ Order Model ပုံစံအတိုင်း Loop ပတ်သိမ်းမည်
        for cart_item in cart_items:
            Order.objects.create(
                item=cart_item.item,
                amount=cart_item.quantity,
                price=cart_item.item.sale_price,
                discount=0.00,
                order_status='pending',
                created_by=request.user
            )
            
            # ပစ္စည်းလက်ကျန် (Stock) နုတ်ခြင်း
            if hasattr(cart_item.item, 'amount') and cart_item.item.amount >= cart_item.quantity:
                cart_item.item.amount -= cart_item.quantity
                cart_item.item.save()
        
        # ဝယ်ယူမှု ပြီးမြောက်၍ ခြင်းတောင်းကို ရှင်းထုတ်ခြင်း
        cart_items.delete()
        request.session['cart_items_count'] = 0
        
        return redirect('order_success') # Success View ဆီ သွားခိုင်းမည်
        
    return redirect('checkout_view')


@login_required
def order_success(request):
    """ အော်ဒါတင်ခြင်း အောင်မြင်ကြောင်း သီးသန့်ပြသမည့် View """
    return render(request, 'order_success.html')

@login_required
def order_index(request):
    orders = Order.objects.filter(created_by=request.user)
    paginator = Paginator(orders, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # print(f'\n \n \n {page_obj}\n \n \n')
    return render(request, 'order/index.html', {'orders': page_obj})

@login_required
def order_dash(request):
    orders = Order.objects.all()
    paginator = Paginator(orders, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # print(f'\n \n \n {page_obj}\n \n \n')
    return render(request, 'order/dash.html', {'orders': page_obj})

def order_test(request, pk):
    order = Order.objects.filter(pk=pk).first()
    if order:
        order.order_status = request.GET.get('status')
        order.save()
        return redirect('order_dash')
    return HttpResponse(pk)




    