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
class AddRequirementForm(forms.Form):
    name = forms.CharField(required=True,max_length=50,min_length=1,error_messages={'required':'请输入需求名称'})
    belong_version = forms.IntegerField(required=True,error_messages={'required':'请输入需求名称'})
    creator = forms.CharField(required=False)
    solver = forms.CharField(required=False)
    tester = forms.CharField(required=False)
    detail = UEditorField(label="详情", width=1000, height=400, toolbars="full", imagePath="requirement/ueditor/", filePath="requirement/ueditor/",upload_settings={"imageMaxSize":5000000},settings={})
    file = forms.FileField(required=False)

class ModifyRequirementForm(forms.Form):
    name = forms.CharField(required=True,max_length=50,min_length=1,error_messages={'required':'请输入需求名称'})
    belong_version = forms.IntegerField(required=False)
    creator = forms.CharField(required=False)
    solver = forms.CharField(required=False)
    tester = forms.CharField(required=False)
    detail = UEditorField(label="详情",width=1000, height=400, toolbars="full", imagePath="requirement/ueditor/", filePath="requirement/ueditor/",upload_settings={"imageMaxSize":5000000},settings={})
    file = forms.FileField(required=False)

class RequirementDetailForm(forms.Form):
    name = forms.CharField(required=True,max_length=50,min_length=1,error_messages={'required':'请输入需求名称'})
    belong_version = forms.IntegerField(required=False)
    creator = forms.CharField(required=False)
    solver = forms.CharField(required=False)
    tester = forms.CharField(required=False)
    detail = UEditorField(label="详情",width=1000, height=400, toolbars="full", imagePath="requirement/ueditor/", filePath="requirement/ueditor/",upload_settings={"imageMaxSize":5000000},settings={})
    file = forms.FileField(required=False)
