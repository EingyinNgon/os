from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Category, UserProfile, SubCategory

def is_admin(user):
    return user.is_superuser

@login_required(login_url='login')
def index(request):
    return render(request, 'index.html')

@login_required(login_url='login')
def user_list(request):
    # print(request.user.is_superuser)
    if request.user.is_superuser:
        users = User.objects.all().select_related('userprofile').order_by('-date_joined')
        return render(request, 'user_list.html', {'users': users})
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
        
        # ၂။ UserProfile Table အတွက် Data ယူမယ်
        phone = request.POST.get('phone_no')
        address = request.POST.get('address')
        vantor = request.POST.get('vantor')
        
        try: 
            user = User.objects.create_user(username=username, password=password, email=email)

            # Signal က ဆောက်ပေးလိုက်တဲ့ Profile ကိုပဲ ပြန်ယူပြီး အချက်အလက်ဖြည့်မယ်
            profile = user.userprofile  
            profile.phone = request.POST.get('phone_no')
            profile.address = request.POST.get('address')
            profile.save()
                    
            return redirect('user_list')
        except Exception as e:
            return render(request, 'add_user.html')
        
    return render(request, 'add_user.html')

@login_required
@user_passes_test(is_admin)
def user_detail(request, pk):
    # ID နဲ့ ရှာမယ်၊ မရှိရင် 404 Error ပေးမယ်
    user_obj = get_object_or_404(User, pk=pk)
    return render(request, 'user_detail.html', {'user_obj': user_obj})

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

    return render(request, 'update_user.html', {'user_obj': user_obj})

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
    
    return render(request, 'add_category.html')

@login_required
@user_passes_test(is_admin)   
def category_list(request):
   # ဖျက်မထားတဲ့ Category တွေကိုပဲ ယူမယ်
    categories = Category.objects.filter(is_deleted=False).order_by('-created_at')
    return render(request, 'category_list.html', {'categories': categories})

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
    return render(request, 'edit_category.html', {'category': category})

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
    return render(request, 'add_subcategory.html', {'categories': categories})

@login_required
@user_passes_test(is_admin)
def subcategory_list(request):
    subcategories = SubCategory.objects.filter(is_deleted=False).order_by('-created_at')
    return render(request, 'subcategory_list.html', {'subcategories': subcategories})

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
    return render(request, 'edit_subcategory.html', {
        'subcategory': sub, 
        'categories': categories
    })