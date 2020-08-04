# Create your models here.
from django.db import models
from mptt.models import MPTTModel
from DjangoUeditor.models import UEditorField
# Create your models here.
from requirement.models import RequirementInfo
from manager.models import ProjectInfo,VersionInfo,DepartmentInfo
from datetime import datetime
import django.utils.timezone as timezone

class BugInfo(models.Model):
    """
    Bugs:
    """
    belong_version = models.ForeignKey(VersionInfo,verbose_name="所属版本",on_delete=models.CASCADE)
    belong_requirement = models.ForeignKey(RequirementInfo, verbose_name="所属需求",on_delete=models.CASCADE,null=True)
    name = models.CharField(max_length=50, verbose_name="Bug标题", default="")
    detail = UEditorField(verbose_name="Bug详情",width=100, height=400, imagePath="bugs/ueditor/",filePath="bugs/ueditor/", default='')
    reporter = models.CharField(max_length=10, verbose_name="提单人", default="")
    solver = models.CharField(max_length=10, verbose_name="指派给", default="")
    level = models.CharField(max_length=10,verbose_name="优先级",choices=(("zm","致命"),("yz","严重"),("yb","一般"),("ts","提示")),default="yb")
    env = models.CharField(max_length=50,verbose_name="环境",choices=(("test","测试环境"),("gray","灰度环境"),("online","线上环境")),default="test")
    add_time = models.DateField(default=datetime.now, verbose_name="添加时间")
    update_time = models.DateField(default=datetime.now, verbose_name="修改时间")
    status = models.CharField(verbose_name="用例状态", choices=(("Open", "打开"), ("ReOpen", "重新打开"),("Fixed", "已解决"), ("Rejected", "无需解决"),("Closed", "已关闭")),max_length=10,default="Open")
    designer = models.CharField(max_length=50, verbose_name="设计者", default="")
    modifier = models.CharField(max_length=50, verbose_name="修改者", default="")
    add_time = models.DateTimeField(default=timezone.now, verbose_name="添加时间")
    update_time = models.DateTimeField(default=timezone.now, verbose_name="修改时间")
    class Meta:
        verbose_name = "bug信息"
        verbose_name_plural = verbose_name

    def __srt__(self):
        return self.name

class BugRecords(models.Model):
    """
    Bug操作记录:
    """
    belong_bug = models.ForeignKey(BugInfo, verbose_name="所属Bug", on_delete=models.CASCADE)
    operator = models.CharField(max_length=10, verbose_name="操作者", default="")
    desc = models.CharField(max_length=50, verbose_name="操作说明", default="")
    status_change = models.CharField(max_length=50, verbose_name="状态变更", default="")
    add_time = models.DateField(default=datetime.now, verbose_name="添加时间")
    update_time = models.DateField(default=datetime.now, verbose_name="修改时间")

    class Meta:
        verbose_name = " Bug操作记录"
        verbose_name_plural = verbose_name

    def __srt__(self):
        return self.desc
