# -*- coding: utf-8 -*-
__author__ = 'bobby'
__date__ = '2016/10/29 23:01'
from django import forms
from DjangoUeditor.models import UEditorField
from DjangoUeditor.forms import UEditorField

from captcha.fields import CaptchaField
from django.core.exceptions import ValidationError


# class DepartmentInfoForm(forms.Form):
#     name = forms.CharField(required=True)
class AddBugForm(forms.Form):
    name = forms.CharField(required=True,max_length=50,min_length=1,error_messages={'required':'请输入需求名称'})
    solver = forms.CharField(required=True,error_messages={'required':'请输入需求名称'})
    reporter = forms.CharField(required=False)
    detail = UEditorField(label="详情",width=1000, height=400, toolbars="full", imagePath="bugs/ueditor/", filePath="requirement/ueditor/",upload_settings={"imageMaxSize":5000000},settings={})
    level = forms.CharField(required=True)

class ModifyBugForm(forms.Form):
    name = forms.CharField(required=True,max_length=50,min_length=1,error_messages={'required':'请输入需求名称'})
    solver = forms.CharField(required=True,error_messages={'required':'请输入需求名称'})
    tester = forms.CharField(required=False)
    detail = UEditorField(label="详情",width=1000, height=400, toolbars="full", imagePath="bugs/ueditor/", filePath="requirement/ueditor/",upload_settings={"imageMaxSize":5000000},settings={})
    level = forms.CharField(required=True)

class BugDetailForm(forms.Form):
    name = forms.CharField(required=True,max_length=50,min_length=1,error_messages={'required':'请输入需求名称'})
    solver = forms.CharField(required=True,error_messages={'required':'请输入需求名称'})
    tester = forms.CharField(required=False)
    detail = UEditorField(label="详情",width=1000, height=400, toolbars="full", imagePath="bugs/ueditor/", filePath="requirement/ueditor/",upload_settings={"imageMaxSize":5000000},settings={})
    level = forms.CharField(required=True)
