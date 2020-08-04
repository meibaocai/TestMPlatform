# -*- coding: utf-8 -*-
from django import forms
from captcha.fields import CaptchaField
from django.core.exceptions import ValidationError


# class DepartmentInfoForm(forms.Form):
#     name = forms.CharField(required=True)

class AddProjectForm(forms.Form):
    project_name = forms.CharField(required=True,max_length=50,min_length=1,error_messages={'required':'请输入项目名称'})
    department_id = forms.CharField(required=True)
    project_desc = forms.CharField(required=True,max_length=50,min_length=1,error_messages={'required':'请输入项目描述'})

class ModifyProjectFrom(forms.Form):
    project_name = forms.CharField(required=True,max_length=50,min_length=1,error_messages={'required':'请输入项目名称'})
    department_id = forms.CharField(required=True)
    project_desc = forms.CharField(required=True,max_length=50,min_length=1,error_messages={'required':'请输入项目描述'})

class AddVersionForm(forms.Form):
    version_name = forms.CharField(required=True, min_length=1,max_length=50,error_messages={'required':'请输入版本名称'})
    version_desc = forms.CharField(required=True,max_length=50,min_length=1,error_messages={'required':'请输入版本描述'})
    belong_project = forms.CharField(required=True)

class ModifyVersionForm(forms.Form):
    version_name = forms.CharField(required=True,max_length=50,min_length=1,error_messages={'required':'请输入版本名称'})
    belong_project = forms.CharField(required=True)
    version_desc = forms.CharField(required=True,max_length=50,min_length=1,error_messages={'required':'请输入版本描述'})

class AddServiceForm(forms.Form):
    name = forms.CharField(required=True,max_length=50,min_length=1,error_messages={'required':'请输入服务名称'})
    desc = forms.CharField(required=True,max_length=50,min_length=1,error_messages={'required':'请输入服务描述'})

class ModifyServiceFrom(forms.Form):
    name = forms.CharField(required=True,max_length=50,min_length=1,error_messages={'required':'请输入服务名称'})
    status = forms.CharField(required=True,error_messages={'required':'请选择服务状态'})
    desc = forms.CharField(required=True,max_length=50,min_length=1,error_messages={'required':'请输入服务描述'})


