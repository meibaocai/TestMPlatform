from django.db import models
from mptt.models import MPTTModel

# Create your models here.
from manager.models import ProjectInfo,VersionInfo,DepartmentInfo,ServiceInfo
from requirement.models import RequirementInfo
from datetime import datetime
import django.utils.timezone as timezone
from DjangoUeditor.models import UEditorField

# Api CI环境
class EnvInfo(models.Model):
    env_name = models.CharField(max_length=20, verbose_name="环境名称",default="")
    base_url = models.CharField(max_length=50,verbose_name="base_url",null=False)
    belong_project = models.ForeignKey(ProjectInfo,verbose_name="所属项目",on_delete=models.CASCADE)
    desc = models.CharField(max_length=50, verbose_name="环境描述",default="")
    add_time = models.DateTimeField(default=timezone.now, verbose_name="添加时间")


    class Meta:
        verbose_name = "API环境"
        verbose_name_plural = verbose_name

    def __srt__(self):
        return self.env_name

# 接口用例
class ApiCaseInfo(models.Model):
    api_name = models.CharField(max_length=50, verbose_name="api接口用例名称", default="")
    api_method = models.CharField(max_length=50, verbose_name="api接口Method", default="")
    belong_project_id = models.CharField(verbose_name="关联项目ID", max_length=50, null=False)
    belong_service = models.ForeignKey(ServiceInfo, verbose_name="所属服务", on_delete=models.CASCADE)
    belong_env = models.ForeignKey(EnvInfo,verbose_name="关联环境ID",null=True, db_constraint=False, on_delete=models.SET_NULL)
    designer = models.CharField(max_length=50, verbose_name="设计者", default="")
    modifier = models.CharField(max_length=50, verbose_name="修改者", default="")
    type = models.CharField(verbose_name="用例类型", choices=(("0", "前后置操作"), ("1", "CI"),("2", "非CI"),("3", "删除")), max_length=10, default="1")
    pre_operation = models.CharField(max_length=50, verbose_name="前置操作", default="")
    # api_request 字段中包含请求头headers、url、method、请求方法，GET、POST...，请求消息体data,参数化即可数据池，校验，
    run_after_operation = models.CharField(max_length=100, verbose_name="执行后操作", default="")
    after_operation = models.CharField(max_length=50, verbose_name="后置操作", default="")
    # status = models.CharField(verbose_name="用例状态", choices=(("0", "删除"), ("1", "正常")), max_length=5, default="1")
    api_request = models.TextField('请求信息', null=False)
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")
    update_time = models.DateTimeField(default=datetime.now, verbose_name="修改时间")

    class Meta:
        verbose_name = "api用例"
        verbose_name_plural = verbose_name

    def __srt__(self):
        return self.name

# 前后置操作
class OperationInfo(models.Model):
    name = models.CharField(max_length=50, verbose_name="操作名称",default="")
    belong_project_id = models.CharField(verbose_name="关联项目ID",max_length=10, null=False,default="")
    belong_env = models.ForeignKey(EnvInfo,verbose_name="关联环境ID",null=True,db_constraint=False,on_delete=models.SET_NULL)
    designer = models.CharField(max_length=50, verbose_name="设计者", default="")
    modifier = models.CharField(max_length=50, verbose_name="修改者", default="")
    type = models.CharField(verbose_name="操作类型", choices=(("0", "用例"), ("1", "SQL"),("2", "等待")),max_length=10,default="0")
    operation = models.TextField('请求信息', null=False)
    related_case = models.ForeignKey(ApiCaseInfo,verbose_name="关联用例ID",null=True,db_constraint=False,on_delete=models.SET_NULL)
    status = models.CharField(verbose_name="用例状态", choices=(("0", "删除"), ("1", "正常")), max_length=5, default="1")
    desc = models.CharField(max_length=100, verbose_name="环境描述",default="")
    add_time = models.DateTimeField(default=timezone.now, verbose_name="添加时间")
    update_time = models.DateTimeField(default=timezone.now, verbose_name="修改时间")

    class Meta:
        verbose_name = "前后置操作"
        verbose_name_plural = verbose_name

    def __srt__(self):
        return self.name

# 全局参数
class GlobalParameterInfo(models.Model):
    name = models.CharField(max_length=50, verbose_name="参数名称",default="")
    param_type = models.CharField(verbose_name="参数类型", choices=(("1", "KEY-VALUE类型"), ("2", "SQL类型"),("3", "测试用例类型")),max_length=10,default="1")
    param_content = models.CharField(max_length=1024, verbose_name="参数内容",default="")
    value = models.CharField(max_length=100, verbose_name="参数值",default="")
    related_case = models.ForeignKey(ApiCaseInfo,verbose_name="关联用例ID",null=True,db_constraint=False,on_delete=models.SET_NULL)
    desc = models.CharField(max_length=50, verbose_name="参数描述", default="")
    belong_env = models.ForeignKey(EnvInfo,verbose_name="关联环境ID", null=True,db_constraint=False,on_delete=models.SET_NULL)
    belong_project_id = models.CharField(verbose_name="关联项目ID", max_length=50, null=False,default="")
    add_time = models.DateTimeField(default=timezone.now, verbose_name="添加时间")
    update_time = models.DateTimeField(default=timezone.now, verbose_name="修改时间")

    class Meta:
        verbose_name = "全局参数"
        verbose_name_plural = verbose_name

    def __srt__(self):
        return self.name

# 局部参数
class LocalParameterInfo(models.Model):
    name = models.CharField(max_length=50, verbose_name="参数名称",default="")
    value = models.CharField(max_length=100, verbose_name="参数值",default="")
    desc = models.CharField(max_length=50, verbose_name="参数描述", default="")
    belong_case = models.ForeignKey(ApiCaseInfo,verbose_name="所属api用例",db_constraint=False,on_delete=models.CASCADE)
    belong_project_id = models.CharField(verbose_name="关联项目ID",max_length=10, null=False,default="")
    belong_env_id = models.CharField(verbose_name="关联环境ID", max_length=10, null=False,default="")
    add_time = models.DateTimeField(default=timezone.now, verbose_name="添加时间")
    update_time = models.DateTimeField(default=timezone.now, verbose_name="修改时间")

    class Meta:
        verbose_name = "局部参数"
        verbose_name_plural = verbose_name

    def __srt__(self):
        return self.name

# CI 执行计划
class RunApiPlanInfo(models.Model):
    name = models.CharField(max_length=100, verbose_name="API执行计划名称", default="")
    run_batch = models.CharField(max_length=50, verbose_name="运行批次号", default="")
    belong_project_id = models.CharField(verbose_name="关联项目ID", max_length=50, null=False)
    run_user = models.CharField(max_length=50, verbose_name="执行者", default="")
    case_num = models.IntegerField(verbose_name="用例总数",null=True, blank=True, default=None)
    success_num = models.IntegerField(verbose_name="成功数", null=True, blank=True, default=None)
    fail_num = models.IntegerField(verbose_name="失败数", null=True, blank=True, default=None)
    success_ratio = models.FloatField(verbose_name="成功率", null=True, blank=True, default=None)
    start_time = models.DateTimeField(default=datetime.now, verbose_name="开始时间")
    end_time = models.DateTimeField(default=datetime.now, verbose_name="结束时间")

# CI执行记录
class RunApiResultInfo(models.Model):
    api_name = models.CharField(max_length=50, verbose_name="API执行记录名称", default="")
    type = models.CharField(verbose_name="类型", choices=(("1", "单个"), ("2", "批量")), max_length=10, default="1")
    run_batch = models.CharField(max_length=50, verbose_name="运行批次号", default="")
    belong_project_id = models.CharField(verbose_name="关联项目ID", max_length=50, null=False)
    related_case = models.ForeignKey(ApiCaseInfo, verbose_name="关联用例ID", null=True, db_constraint=False, on_delete=models.SET_NULL)
    belong_env = models.ForeignKey(EnvInfo, verbose_name="关联环境ID", null=True, db_constraint=False, on_delete=models.SET_NULL)
    belong_service = models.ForeignKey(ServiceInfo, verbose_name="所属服务", null=True, db_constraint=False, on_delete=models.SET_NULL)
    file_path = models.FileField(upload_to="api/logs/")
    detail = models.TextField('执行详情', null=False)
    status = models.CharField(verbose_name="执行状态", choices=(("0", "失败"), ("1", "成功")), max_length=10, default="1")
    start_time = models.DateTimeField(default=datetime.now, verbose_name="开始时间")
    end_time = models.DateTimeField(default=datetime.now, verbose_name="结束时间")

