from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        # User ဖြည့်ရမည့် field များသာ ထည့်ပါ
        fields = ['phone_no', 'address', 'vantor']

        # UI လှပစေရန် styling ထည့်နိုင်ပါသည်
        widgets = {
            'phone_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '09...'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'vantor': forms.TextInput(attrs={'class': 'form-control'}),
        }
class RegisterForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone_no = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'class': 'form-control'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    vantor = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    # Password နှစ်ခု တူ/မတူ စစ်ဆေးတဲ့ Logic
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise ValidationError("Password နှစ်ခု မတူညီပါဘူးခင်ဗျာ။")
        return cleaned_data

class LoginForm(forms.Form):
    # Username သို့မဟုတ် Email နှစ်သက်ရာနဲ့ Login ဝင်နိုင်ဖို့ label ကို ပြောင်းထားပါတယ်
    username_or_email = forms.CharField(label="Username or Email", widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))