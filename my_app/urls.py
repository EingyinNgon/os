from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(
    template_name='login.html', 
    redirect_authenticated_user=True  # ဒါလေးထည့်လိုက်ရင် Login ဝင်ထားသူကို တန်းကျော်သွားစေမှာပါ
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
    path('register/', views.register_user, name='register'),
    path('users/', views.user_list, name='user_list'),
    path('users/add/', views.add_user, name='add_user'),
    path('users/<int:pk>/', views.user_detail, name='user_detail'),
    path('users/update/<int:pk>/', views.update_user, name='update_user'),
    path('users/delete/<int:pk>/', views.delete_user, name='delete_user'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.add_category, name='add_category'),
    path('categories/edit/<int:pk>/', views.edit_category, name='edit_category'),
    path('categories/delete/<int:pk>/', views.delete_category, name='delete_category'),
    path('subcategories/', views.subcategory_list, name='subcategory_list'),
    path('subcategories/add/', views.add_subcategory, name='add_subcategory'),
    path('subcategories/edit/<int:pk>/', views.edit_subcategory, name='edit_category_sub'), 
    path('subcategories/delete/<int:pk>/', views.delete_subcategory, name='delete_subcategory'),
    path('', views.index, name='index')
]