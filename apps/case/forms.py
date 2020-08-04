from django import forms
from DjangoUeditor.models import UEditorField
from DjangoUeditor.forms import UEditorField

class AddXMindCaseForm(forms.Form):
    name = forms.CharField(required=True,max_length=50,min_length=1,error_messages={'required':'请输入用例主题'})
    belong_project = forms.IntegerField(required=True)
    belong_Service = forms.IntegerField(required=True)
    detail = UEditorField(label="详情",width=600, height=300, toolbars="full", imagePath="case/ueditor/", filePath="case/ueditor/",upload_settings={"imageMaxSize":5000000},settings={})

class ModifyXMindCaseForm(forms.Form):
    name = forms.CharField(required=True,max_length=50,min_length=1,error_messages={'required':'请输入用例主题'})
    belong_project = forms.IntegerField(required=True)
    belong_Service = forms.IntegerField(required=True)
    detail = UEditorField(label="详情",width=600, height=300, toolbars="full", imagePath="case/ueditor/", filePath="case/ueditor/",upload_settings={"imageMaxSize":5000000},settings={})

class XMindCaseDetailForm(forms.Form):
    name = forms.CharField(required=True,max_length=50,min_length=1,error_messages={'required':'请输入用例主题'})
    belong_project = forms.IntegerField(required=True)
    belong_Service = forms.IntegerField(required=True)
    detail = UEditorField(label="详情",width=600, height=300, toolbars="full", imagePath="case/ueditor/", filePath="case/ueditor/",upload_settings={"imageMaxSize":5000000},settings={})
