from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
# default table ဖြင့်ဆက်သွယ်ခြင်း
# from .models import Category


# User ဆောက်ပြီးတာနဲ့ ဒီ function က အလိုအလျောက် အလုပ်လုပ်မှာပါ
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

# (၃) Order ရဲ့ အခြေအနေ (ဥပမာ- Pending, Completed, Cancelled)
ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Success'),
        ('cancelled', 'Cancelled'),
    ]

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)    
    phone_no = models.CharField(max_length=15)
    # int သည် 1 to 9 အထိသာဖြစ်သဖြင့် charfield ကို အသုံးပ​ြုခြင်းဖြစ်သညါ    
    address = models.TextField()

    is_vendor = models.BooleanField(default=False) # 'vantor' string အစား BooleanField ပြောင်းလိုက်ပါပြီ
    shop_logo = models.ImageField(upload_to='vendors/', null=True, blank=True) # Vendor ပုံသိမ်းရန်
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    descriptions = models.TextField(blank=True, null=True)
    
    # Soft Delete flag (တကယ်မဖျက်ဘဲ ဖျက်လိုက်သယောင် လုပ်ထားဖို့)
    is_deleted = models.BooleanField(default=False)
    
    # ဘယ်သူ create လုပ်ခဲ့သလဲဆိုတာ သိဖို့ Foreign Key ချိတ်တာ
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        # ဒါက အရေးကြီးပါတယ်။ ဥပမာ- "မောင်မောင်" ဆိုတဲ့ Admin က "Electronics" ဆိုတဲ့ Category ကို ဆောက်ခဲ့တယ်။ 
        # နောက်ပိုင်းမှာ "မောင်မောင်" အလုပ်ထွက်သွားလို့ သူ့ User Account ကို ဖျက်လိုက်ရင် "Electronics" ဆိုတဲ့ Category ကိုပါ လိုက်ဖျက်မှာလား?
        # မဖျက်စေချင်ဘူးဆိုရင် SET_NULL ကို သုံးပါတယ်။
        # ဒါဆိုရင် created_by နေရာမှာ "ဘယ်သူမှန်းမသိတော့ပါ (Null)" လို့ပဲ ပြောင်းသွားပြီး Category ကတော့ ကျန်နေခဲ့မှာပါ။
        null=True,
        # SET_NULL သုံးရင် ဒါလေး ပါကိုပါရမယ်။ "ဒီ Column မှာ ဘာမှမရှိဘဲ (NULL) ဖြစ်ခွင့်ပေးတယ်" လို့ ခွင့်ပြုချက်ပေးတာပါ။ 
        related_name='categories_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class Item(models.Model):
    # (၁) Relationship များ
    # Item တစ်ခုက SubCategory တစ်ခုအောက်မှာ ရှိမယ်
    sub_category = models.ForeignKey(
        'SubCategory', 
        on_delete=models.CASCADE, 
        related_name='items'
    )
    # ဘယ်သူက ဒီ Item ကို စာရင်းသွင်းတာလဲ
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='items_created'
    )

    # (၂) အချက်အလက်များ
    name = models.CharField(max_length=200)
    amount = models.IntegerField(default=0)      # လက်ကျန်အရေအတွက်
    size = models.CharField(max_length=50, blank=True, null=True) # ဥပမာ- Large, 42, 10-inch
    
    # (၃) ဈေးနှုန်းပိုင်းဆိုင်ရာ (DecimalField သုံးတာ ပိုကောင်းပါတယ်)
    buy_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # (၄) Discount ပိုင်း
    is_discount = models.BooleanField(default=False)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # (၅) အခြေအနေပြချက်များ
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='items/', null=True, blank=True)

    def __str__(self):
        return self.name  

def generate_order_number():
    return "SOME_GENERATED_NUMBER" 

class Order(models.Model):
    order_number = models.CharField(default='PYG-0000', max_length=20)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='orders_processed'
    )
    shipping_phone = models.CharField(max_length=15)
    shipping_address = models.TextField()

class OrderDetail(models.Model):
    # (၁) ဘယ်ပစ္စည်းကို ရောင်းတာလဲ (Relationship)
    item = models.ForeignKey(
        'Item', 
        on_delete=models.PROTECT, # ပစ္စည်းစာရင်းကို ဖျက်လိုက်ပေမယ့် ရောင်းရတဲ့စာရင်း မပျက်စေချင်လို့ PROTECT သုံးတာ ပိုကောင်းပါတယ်
        related_name='orders_detail'
    )

    order_id =  models.ForeignKey(
        'Order', 
        on_delete=models.PROTECT, # ပစ္စည်းစာရင်းကို ဖျက်လိုက်ပေမယ့် ရောင်းရတဲ့စာရင်း မပျက်စေချင်လို့ PROTECT သုံးတာ ပိုကောင်းပါတယ်
        related_name='order'
    )
    
    # (၂) အရောင်းအချက်အလက်များ
    amount = models.IntegerField() # ဘယ်နှခုရောင်းရသလဲ
    price = models.DecimalField(max_digits=10, decimal_places=2)    # ရောင်းရစဉ်က ဈေးနှုန်း
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) # ရောင်းရစဉ်က လျှော့ဈေး
    
    
    order_status = models.CharField(
        max_length=20, 
        choices=ORDER_STATUS_CHOICES, 
        default='pending'
    )
    
    # (၄) Audit Fields
    is_deleted = models.BooleanField(default=False)
    
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} - {self.item.name}"
#     self.id: ဒီ Order ရဲ့ ID နံပါတ် (ဥပမာ - 105)
#     self.item.name: ဒီ Order ထဲမှာပါတဲ့ ပစ္စည်းရဲ့ နာမည် (Foreign Key ကနေတစ်ဆင့် လှမ်းယူတာပါ)
#     ရလဒ် (Result):
#     Admin Panel မှာ ကြည့်လိုက်ရင် Order 105 - iPhone 15 ဆိုပြီး ဖတ်ရလွယ်တဲ့ စာသားအနေနဲ့ မြင်ရမှာ ဖြစ်ပါတယ်။

class SubCategory(models.Model):
    # ဘယ် Category အောက်ကလဲဆိုတာ ချိတ်တာ (ဒါက အဓိကပဲ!)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    
    name = models.CharField(max_length=100)
    descriptions = models.TextField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category.name} -> {self.name}"
    
# ၁။ Cart Table (User တစ်ယောက်ချင်းစီရဲ့ ခြင်းတောင်းမကြီး)
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user.username}"

    # Cart ထဲက ပစ္စည်းတွေအားလုံးရဲ့ စုစုပေါင်းတန်ဖိုးကို Auto တွက်ပေးမယ့် Function 
    @property
    def total_price(self):
        return sum(item.subtotal for item in self.cart_items.all())

# ၂။ CartItem Table (ခြင်းတောင်းထဲက ပစ္စည်းတစ်ခုချင်းစီနှင့် အရေအတွက်)
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    item = models.ForeignKey('Item', on_delete=models.CASCADE) # သင့်ရဲ့ Item Model နှင့် ချိတ်ခြင်း
    quantity = models.PositiveIntegerField(default=1) # ဝယ်မယ့် အရေအတွက်
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.item.name}"

    # ပစ္စည်းတစ်ခုချင်းစီရဲ့ (ရောင်းဈေး x အရေအတွက်) ကို တွက်ပေးတာပါ
    @property
    def subtotal(self):
        return self.item.sale_price * self.quantity