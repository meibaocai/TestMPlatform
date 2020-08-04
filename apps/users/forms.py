# -*- coding: utf-8 -*-
__author__ = 'bobby'
__date__ = '2016/10/29 23:01'
from django import forms
from django.forms import widgets
from captcha.fields import CaptchaField
from django.core.exceptions import ValidationError

from .models import UserProfile

class LoginForm(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(required=True, min_length=5)


class RegisterForm(forms.Form):
    username = forms.CharField(required=True, min_length=5)
    password = forms.CharField(required=True, min_length=5)
    rpassword = forms.CharField(required=True, min_length=5)
    email = forms.EmailField(required=True,min_length=4,max_length=20,error_messages={
        "required": '邮箱不能为空',
        "invalid": "邮箱格式错误",
    })
    mobile = forms.CharField(label='手机号',
                widget=widgets.TextInput(attrs={"class": "form-control"}))
    # captcha = CaptchaField(error_messages={"invalid":u"验证码错误"})

class ForgetForm(forms.Form):
    email = forms.EmailField(required=True)
    # captcha = CaptchaField(error_messages={"invalid":u"验证码错误"})


class ModifyPwdForm(forms.Form):
    password1 = forms.CharField(required=True, min_length=5)
    password2 = forms.CharField(required=True, min_length=5)


# class UploadImageForm(forms.ModelForm):
#     class Meta:
#         model = UserProfile
#         fields = ['image']
#
#
# class UserInfoForm(forms.ModelForm):
#     class Meta:
#         model = UserProfile
#         fields = ['gender', 'birday', 'address', 'mobile']

