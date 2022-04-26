from django.db import models
from mptt.models import MPTTModel

# Create your models here.
from manager.models import ProjectInfo,VersionInfo,DepartmentInfo,ServiceInfo
from requirement.models import RequirementInfo
from datetime import datetime
import django.utils.timezone as timezone
from DjangoUeditor.models import UEditorField



# 普通产品库用例
class TestCase(models.Model):
    name = models.CharField(max_length=200, verbose_name="用例主题", default="")
    parent_id = models.IntegerField(verbose_name='父目录', null=True)
    # parent_area = models.ForeignKey('self', verbose_name='父目录', null=True, blank=True, related_name='children',on_delete=models.CASCADE)
    jb = models.CharField(verbose_name="用例级别", choices=(("level0", "level0"), ("level1", "level1"), ("level2", "level2"), ("level3", "level3"), ("level4", "level4")), max_length=10, default="level1")
    precondition = models.TextField(verbose_name="预置条件", default="")
    operation = models.TextField(verbose_name="操作步骤", default="")
    expect_result = models.TextField(verbose_name="期望结果", default="")
    case_desc = models.TextField(verbose_name="用例备注", default="")
    designer = models.CharField(max_length=50, verbose_name="设计者", default="")
    modifier = models.CharField(max_length=50, verbose_name="修改者", default="")
    add_time = models.DateTimeField(default=timezone.now, verbose_name="添加时间")
    update_time = models.DateTimeField(default=timezone.now, verbose_name="修改时间")
    status = models.CharField(verbose_name="用例状态", choices=(("0", "删除"), ("1", "正常")), max_length=5, default="1")
    type = models.CharField(verbose_name="类型", choices=(("ml", "目录"), ("yl", "用例")), max_length=5, default="")
    belong_project = models.ForeignKey(ProjectInfo, verbose_name=u"所属项目", null=True, db_constraint=False, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = "用例信息"
        verbose_name_plural = verbose_name

    class MPTTMeta:
        parent_attr = 'parent_area'

    def __srt__(self):
        return self.name


# 产品库用例临时表
class TestCase_tmp(models.Model):
    name = models.CharField(max_length=200, verbose_name="用例主题", default="")
    parent_id = models.IntegerField(verbose_name='父目录', null=True)
    # parent_area = models.ForeignKey('self', verbose_name='父目录', null=True, blank=True, related_name='children',on_delete=models.CASCADE)
    jb = models.CharField(verbose_name="用例级别", choices=(("level0", "level0"), ("level1", "level1"), ("level2", "level2"), ("level3", "level3"), ("level4", "level4")), max_length=10, default="level1")
    precondition = models.TextField(verbose_name="预置条件", default="")
    operation = models.TextField(verbose_name="操作步骤",default="")
    expect_result = models.TextField(verbose_name="期望结果",default="")
    case_desc = models.TextField(verbose_name="用例备注", default="")
    designer = models.CharField(max_length=50, verbose_name="设计者", default="")
    modifier = models.CharField(max_length=50, verbose_name="修改者", default="")
    add_time = models.DateTimeField(default=timezone.now, verbose_name="添加时间")
    update_time = models.DateTimeField(default=timezone.now, verbose_name="修改时间")
    status = models.CharField(verbose_name="用例状态", choices=(("0", "删除"), ("1", "正常")), max_length=5, default="1")
    type = models.CharField(verbose_name="类型", choices=(("ml", "目录"), ("yl", "用例")), max_length=5, default="")
    belong_project = models.ForeignKey(ProjectInfo, verbose_name=u"所属项目", null=True, db_constraint=False, on_delete=models.SET_NULL)
    import_batch = models.CharField(max_length=50, verbose_name="导入批次号", default="")

    class Meta:
        verbose_name = "产品库用例临时表"
        verbose_name_plural = verbose_name

    def __srt__(self):
        return self.name

# 普通版本库用例
class VersionCase(models.Model):
    name = models.CharField(max_length=200, verbose_name="用例主题", default="")
    parent_id = models.IntegerField(verbose_name='父目录', null=True)
    # parent_area = models.CharField(verbose_name='父目录',max_length=10, null=True, blank=True,default='')
    jb = models.CharField(verbose_name="用例级别", choices=(("level0", "level0"), ("level1", "level1"), ("level2", "level2"), ("level3", "level3"), ("level4", "level4")), max_length=10, default="level1")
    precondition = models.TextField(verbose_name="预置条件", default="")
    operation = models.TextField(verbose_name="操作步骤",default="")
    expect_result = models.TextField(verbose_name="期望结果",default="")
    case_desc = models.TextField(verbose_name="用例备注", default="")
    designer = models.CharField(max_length=50, verbose_name="设计者", default="")
    modifier = models.CharField(max_length=50, verbose_name="修改者", default="")
    add_time = models.DateTimeField(default=timezone.now, verbose_name="添加时间")
    update_time = models.DateTimeField(default=timezone.now, verbose_name="修改时间")
    status = models.CharField(verbose_name="用例状态", choices=(("0", "删除"), ("1", "正常")), max_length=5, default="1")
    type = models.CharField(verbose_name="类型", choices=(("ml", "目录"), ("yl", "用例")), max_length=5, default="")
    p_case_id = models.IntegerField(verbose_name="关联产品用例库的id", null=True)
    belong_version = models.ForeignKey(VersionInfo, verbose_name=u"所属版本", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "用例信息"
        verbose_name_plural = verbose_name

    class MPTTMeta:
        parent_attr = 'parent_area'

    def __srt__(self):
        return self.name


# 普通版本库用例临时表
class VersionCase_tmp(models.Model):
    name = models.CharField(max_length=200, verbose_name="用例主题", default="")
    parent_id = models.IntegerField(verbose_name='父目录', null=True)
    jb = models.CharField(verbose_name="用例级别", choices=(("level0", "level0"), ("level1", "level1"), ("level2", "level2"), ("level3", "level3"), ("level4", "level4")), max_length=10, default="level1")
    precondition = models.TextField(verbose_name="预置条件", default="")
    operation = models.TextField(verbose_name="操作步骤",default="")
    expect_result = models.TextField(verbose_name="期望结果",default="")
    case_desc = models.TextField(verbose_name="用例备注", default="")
    designer = models.CharField(max_length=50, verbose_name="设计者", default="")
    modifier = models.CharField(max_length=50, verbose_name="修改者", default="")
    add_time = models.DateTimeField(default=timezone.now, verbose_name="添加时间")
    update_time = models.DateTimeField(default=timezone.now, verbose_name="修改时间")
    status = models.CharField(verbose_name="用例状态", choices=(("0", "删除"), ("1", "正常")), max_length=5, default="1")
    type = models.CharField(verbose_name="类型", choices=(("ml", "目录"), ("yl", "用例")), max_length=5, default="")
    p_case_id = models.IntegerField(verbose_name="关联产品用例库的id", null=True)
    belong_version = models.ForeignKey(VersionInfo, verbose_name=u"所属版本", on_delete=models.CASCADE)
    run_batch = models.CharField(max_length=50, verbose_name="导入批次号", default="")

    class Meta:
        verbose_name = "用例信息"
        verbose_name_plural = verbose_name

    def __srt__(self):
        return self.name
# 执行集
class TestCaseSuit(models.Model):
    belong_version = models.ForeignKey(VersionInfo, verbose_name="所属版本", on_delete=models.CASCADE)
    requirement_id = models.CharField(verbose_name="关联需求ID",max_length=10,default="")
    requirement_name = models.CharField(verbose_name="关联需求名称",max_length=50,default="")
    name = models.CharField(max_length=50, verbose_name="执行集名称", default="")
    creator = models.CharField(max_length=50, verbose_name="创建者", default="")
    executor = models.CharField(max_length=50, verbose_name="执行者", default="")
    start_time = models.DateTimeField(default=timezone.now, verbose_name="添加时间")
    end_time = models.DateTimeField(default=timezone.now, verbose_name="修改时间")
    status = models.CharField(verbose_name="执行集状态", choices=(("new", "新建"), ("ongoing", "进行中"), ("finish", "完成"), ("stop", "终止")), max_length=10,default="new")

# 测试用例执行集详情
class TestCaseSuitDetail(models.Model):
    belong_suit = models.ForeignKey(TestCaseSuit, verbose_name="所属执行集", on_delete=models.CASCADE)
    belong_version_case = models.ForeignKey(VersionCase,verbose_name="关联的版本用例",on_delete=models.CASCADE)
    name = models.CharField(max_length=200, verbose_name="用例主题", default="")
    parent_id = models.IntegerField(verbose_name='父目录', null=True)
    type = models.CharField(verbose_name="类型", choices=(("ml", "目录"), ("yl", "用例")), max_length=5, default="yl")
    jb = models.CharField(verbose_name="用例级别", choices=(("level0", "level0"), ("level1", "level1"), ("level2", "level2"), ("level3", "level3"), ("level4", "level4")),max_length=10, default="level1")
    precondition = models.TextField(verbose_name="预置条件", default="")
    operation = models.TextField(verbose_name="操作步骤", default="")
    expect_result = models.TextField(verbose_name="期望结果", default="")
    desc = models.TextField(verbose_name="用例备注", default="")
    remind = models.TextField(verbose_name="执行备注", default="")
    designer = models.CharField(max_length=50, verbose_name="设计者", default="")
    modifier = models.CharField(max_length=50, verbose_name="修改者", default="")
    add_time = models.DateTimeField(default=timezone.now, verbose_name="添加时间")
    update_time = models.DateTimeField(default=timezone.now, verbose_name="修改时间")
    status = models.CharField(verbose_name="用例执行状态", choices=(("New", "未执行"),("Pass", "执行通过"), ("Fail", "执行失败"), ("NG", "无需执行"), ("Block", "执行阻塞")), max_length=10, default="New")

    class Meta:
        verbose_name = "测试用例执行集详情"
        verbose_name_plural = verbose_name

    def __srt__(self):
        return self.name

# 思维导图用例
class XMindCase(models.Model):
    belong_project = models.ForeignKey(ProjectInfo, verbose_name="所属项目", on_delete=models.CASCADE)
    belong_service = models.ForeignKey(ServiceInfo, verbose_name="所属服务", on_delete=models.CASCADE)
    name = models.CharField(max_length=200, verbose_name="用例主题", default="")
    designer = models.CharField(max_length=50, verbose_name="设计者", default="")
    modifier = models.CharField(max_length=50, verbose_name="修改者", default="")
    add_time = models.DateField(default=datetime.now, verbose_name="添加时间")
    update_time = models.DateField(default=datetime.now, verbose_name="修改时间")
    detail = UEditorField(verbose_name="需求详情",width=600, height=300, imagePath="case/ueditor/",filePath="case/ueditor/", default='')
    status = models.CharField(verbose_name="用例状态", choices=(("0", "删除"), ("1", "正常")),max_length=5,  default="1")

    class Meta:
        verbose_name = "思维导图用例"
        verbose_name_plural = verbose_name

    def __srt__(self):
        return self.name
