from django.contrib import admin
from .models import Category, SubCategory, Item, Order, UserProfile

admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Item)
admin.site.register(Order)
admin.site.register(UserProfile)
# Register your models here.
