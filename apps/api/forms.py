# -*- coding: utf-8 -*-
from django import forms
from captcha.fields import CaptchaField
from django.core.exceptions import ValidationError


# class DepartmentInfoForm(forms.Form):
#     name = forms.CharField(required=True)

class AddEnvForm(forms.Form):
    env_name = forms.CharField(required=True, max_length=20,min_length=1,error_messages={'required':'请输入环境名称'})
    base_url = forms.CharField(required=True, max_length=50,min_length=1,error_messages={'required':'请输入环境base_url'})

class ModifyEnvForm(forms.Form):
    env_name = forms.CharField(required=True, max_length=20,min_length=1,error_messages={'required':'请输入环境名称'})
    base_url = forms.CharField(required=True, max_length=50,min_length=1,error_messages={'required':'请输入环境base_url'})

class AddGlobalParameterForm(forms.Form):
    name = forms.CharField(required=True, max_length=20,min_length=1,error_messages={'required':'请输入环境名称'})
    param_type = forms.CharField(required=True,max_length=10,error_messages={'required':'请选择参数类型'})
    value = forms.CharField(required=False, max_length=100)
    param_content = forms.CharField(required=False, max_length=1024)
    related_case_id = forms.CharField(required=False, max_length=10)
    belong_env = forms.IntegerField(required=True, error_messages={'required':'请输入环境名称'})
    desc = forms.CharField(max_length=50)

class ModifyGlobalParameterForm(forms.Form):
    name = forms.CharField(required=True, max_length=20, min_length=1, error_messages={'required':'请输入环境名称'})
    param_type = forms.CharField(required=True, max_length=10, error_messages={'required':'请选择参数类型'})
    value = forms.CharField(required=False, max_length=100)
    param_content = forms.CharField(required=False, max_length=1024)
    related_case_id = forms.CharField(required=False, max_length=10)
    belong_env = forms.IntegerField(required=True, error_messages={'required':'请输入环境名称'})
    desc = forms.CharField(max_length=50)

class AddApiCaseForm(forms.Form):
    api_name = forms.CharField(required=True,max_length=50,min_length=1,error_messages={'required':'请输入接口名称'})
    api_method = forms.CharField(required=True,max_length=50,error_messages={'required':'请选择api接口Method'})
    belong_service = forms.CharField(required=True,max_length=10,error_messages={'required':'请选择所属服务'})
    belong_env_id = forms.CharField(required=True,max_length=50,error_messages={'required':'关联的env_id不能为空'})
    api_request = forms.CharField(required=True,min_length=1,error_messages={'required':'请输入接口名称'})

class ModifyApiCaseForm(forms.Form):
    api_name = forms.CharField(required=True,max_length=50,min_length=1,error_messages={'required':'请输入接口名称'})
    api_method = forms.CharField(required=True,max_length=50,error_messages={'required':'请选择api接口Method'})
    belong_service = forms.CharField(required=True,max_length=10,error_messages={'required':'请选择所属服务'})
    belong_env_id = forms.CharField(required=True,max_length=50,error_messages={'required':'关联的env_id不能为空'})
    api_request = forms.CharField(required=True,min_length=1,error_messages={'required':'请输入接口名称'})

class AddOptsForm(forms.Form):
    name = forms.CharField(required=True,max_length=50, error_messages={'required': '请输入操作名称'})
    type = forms.CharField(required=True, max_length=10, error_messages={'required': '请选择操作类型'})
    related_case = forms.CharField(required=False, max_length=10)
    belong_env = forms.IntegerField(required=True, error_messages={'required': '请输入环境名称'})
    desc = forms.CharField(max_length=50)

class ModifyoOptsForm(forms.Form):
    name = forms.CharField(required=True,max_length=50, error_messages={'required': '请输入操作名称'})
    type = forms.CharField(required=True, max_length=10, error_messages={'required': '请选择操作类型'})
    related_case = forms.CharField(required=False, max_length=10)
    belong_env = forms.IntegerField(required=True, error_messages={'required': '请输入环境名称'})
    desc = forms.CharField(max_length=50)