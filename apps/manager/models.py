from __future__ import unicode_literals
from datetime import datetime
from mptt.models import MPTTModel
from django.db import models

class DepartmentInfo(MPTTModel):
    """
    公司组织架构信息
    """
    name = models.CharField(max_length=20, verbose_name='部门名称',default="")
    parent = models.ForeignKey('self', verbose_name='上级部门', null=True, blank=True, related_name='my_father',on_delete=models.CASCADE)
    creator = models.CharField(max_length=10, verbose_name='创建人',default="admin")
    add_time = models.DateField(default=datetime.now, verbose_name="添加时间")
    class MPTTMeta:
        order_insertion_by = ['name']
    class Meta:
        verbose_name = "公司组织架构信息"
        verbose_name_plural = verbose_name

    def __srt__(self):
        return self.name

class ProjectInfo(models.Model):
    """
    项目信息
    """
    project_name = models.CharField(max_length=50, verbose_name=u"项目名称", default="")
    blong_department = models.ForeignKey(DepartmentInfo,verbose_name="所属部门",on_delete=models.CASCADE,default="")
    project_desc = models.CharField(max_length=50, verbose_name=u"项目描述", default="")
    creator = models.CharField(max_length=10, verbose_name='创建人',default="admin")
    status = models.CharField(verbose_name="项目状态", choices=(("0", "删除"), ("1", "正常"),),max_length=5,default="1")
    add_time = models.DateField(default=datetime.now, verbose_name=u"添加时间")

    class Meta:
        verbose_name = "项目信息"
        verbose_name_plural = verbose_name

    def __srt__(self):
        return self.project_name

class VersionInfo(models.Model):
    """
    项目版本信息
    """
    version_name = models.CharField(max_length=50, verbose_name=u"版本名称", default="")
    belong_project = models.ForeignKey(ProjectInfo, verbose_name=u"所属项目",on_delete=models.CASCADE)
    version_desc = models.CharField(max_length=100, verbose_name=u"版本描述", default="")
    creator = models.CharField(max_length=10, verbose_name='创建人',default="admin")
    status = models.CharField(verbose_name="版本状态", choices=(("0", "删除"), ("1", "正常")), max_length=5, default="1")
    add_time = models.DateField(default=datetime.now, verbose_name=u"添加时间")

    class Meta:
        verbose_name = "版本信息"
        verbose_name_plural = verbose_name

    def __srt__(self):
        return self.version_name

class ServiceInfo(models.Model):
    """
    项目服务信息，用于自动化的服务分组
    """
    name = models.CharField(max_length=50, verbose_name=u"服务名称", default="")
    belong_project = models.ForeignKey(ProjectInfo, verbose_name=u"所属项目",on_delete=models.CASCADE)
    desc = models.CharField(max_length=100, verbose_name=u"服务描述", default="")
    creator = models.CharField(max_length=10, verbose_name='创建人',default="admin")
    add_time = models.DateField(default=datetime.now, verbose_name=u"添加时间")
    status = models.CharField(verbose_name="服务状态", choices=(("0", "删除"), ("1", "正常"),),max_length=5,default="1")

    class Meta:
        verbose_name = "服务信息"
        verbose_name_plural = verbose_name

    def __srt__(self):
        return self.name

