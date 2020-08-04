from django.db import models
from mptt.models import MPTTModel
# Create your models here.
from manager.models import ProjectInfo,VersionInfo,DepartmentInfo
from datetime import datetime
from DjangoUeditor.models import UEditorField
from django.db import models

class RequirementInfo(models.Model):
    """
    需求信息表:
    """
    belong_version = models.ForeignKey(VersionInfo,verbose_name="所属版本",default="",on_delete=models.CASCADE)
    project_id = models.IntegerField(verbose_name="所属项目",default="")
    name = models.CharField(max_length=50, verbose_name="需求名称")
    detail = UEditorField(verbose_name="需求详情", width=600, height=300, toolbars="full", imagePath="requirement/ueditor/", filePath="requirement/ueditor/",upload_settings={"imageMaxSize":5000000},settings={})
    creator = models.CharField(max_length=10, verbose_name="产品", default="")
    solver = models.CharField(max_length=10, verbose_name="需求负责人", default="")
    tester = models.CharField(max_length=10,verbose_name="测试对接人",default="")
    add_time = models.DateField(default=datetime.now, verbose_name="添加时间")
    update_time = models.DateField(default=datetime.now, verbose_name="修改时间")
    status = models.CharField(max_length=10,verbose_name="需求状态", choices=(("0", "删除"), ("1", "新建"), ("2", "开发中"), ("3", "测试验收"), ("4", "验收完成"),("5", "暂停"),), default="1")
    file = models.FileField(verbose_name="附件",upload_to="requirement/file/")

    class Meta:
        verbose_name = "需求信息表"
        verbose_name_plural = verbose_name

    def __srt__(self):
        return self.name

class RequirementTask(models.Model):
    """
    需求任务信息:
    """
    belong_requirement = models.ForeignKey(RequirementInfo,verbose_name="所属需求",on_delete=models.CASCADE)
    name = models.CharField(max_length=50, verbose_name="任务名称", default="")
    detail = UEditorField(verbose_name="需求详情", width=1000, height=400, imagePath="requirement/ueditor/",filePath="bugs/ueditor/", default='')
    creator = models.CharField(max_length=10, verbose_name="创建者", default="")
    owner = models.CharField(max_length=10, verbose_name="任务负责人", default="")
    type = models.CharField(max_length=10,verbose_name="任务类型",choices=(("fx","需求分析"),("sj","需求设计"),("bx","用例编写"),("ps","用例评审"),("kf","开发需求"),("tys","测试验收"),("cys","产品验收"),("qt","其他任务")), default='')
    progress = models.CharField(max_length=10,verbose_name="任务进度",
                                choices=(
                                    ("0", "0%"),
                                    ("5","5%"),
                                    ("10","10%"),
                                    ("20", "20%"),
                                    ("30", "30%"),
                                    ("40", "40%"),
                                    ("50", "50%"),
                                    ("60", "60%"),
                                    ("70", "70%"),
                                    ("80", "80%"),
                                    ("85", "85%"),
                                    ("90", "90%"),
                                    ("95", "95%"),
                                    ("100", "100%")
                                ),default="0"
                                )
    add_time = models.DateField(default=datetime.now, verbose_name="添加时间")
    update_time = models.DateField(default=datetime.now, verbose_name="修改时间")
    status = models.IntegerField(verbose_name="用例状态", choices=(("0", "删除"), ("1", "正常")), default="1")

    class Meta:
        verbose_name = "需求任务信息"
        verbose_name_plural = verbose_name

    def __srt__(self):
        return self.name

class TaskTimes(models.Model):
    """
    任务时间信息:
    """
    belong_task = models.ForeignKey(RequirementTask,verbose_name="所属任务",on_delete=models.CASCADE,max_length=20)
    owner = models.CharField(max_length=10, verbose_name="任务所属者", default="")
    times = models.FloatField(verbose_name="任务耗费时间",default=0.0,max_length=10)
    add_time = models.DateField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "任务时间信息"
        verbose_name_plural = verbose_name

    def __srt__(self):
        return self.times
