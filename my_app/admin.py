from django.contrib import admin
from .models import Category, SubCategory, Item, Order, UserProfile, Cart, CartItem

admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Item)
admin.site.register(Order)
admin.site.register(UserProfile)
admin.site.register(Cart)
admin.site.register(CartItem)
# Register your models here.
