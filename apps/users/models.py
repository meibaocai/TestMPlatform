# _*_ encoding:utf-8 _*_
from __future__ import unicode_literals
from datetime import datetime
from manager.models import ProjectInfo,VersionInfo,DepartmentInfo
from django.db import models
from django.contrib.auth.models import AbstractUser
from PIL import ImageFile


class UserProfile(AbstractUser):
    b_department = models.ForeignKey(DepartmentInfo,verbose_name=u"所属组织",on_delete=models.CASCADE,default=1)
    gender = models.CharField(max_length=6, choices=(("male", u"男"),("female", "女")), default="female")
    address = models.CharField(max_length=50, default=u"")
    mobile = models.CharField(max_length=11, null=True, blank=True)
    image = models.ImageField(upload_to="users/",default=u"image/default.png", max_length=100)
    add_time = models.DateField(default=datetime.now,verbose_name=u"添加时间",)

    class Meta:
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name

    def __srt__(self):
        return self.username

class EmailVerifyRecord(models.Model):
    code = models.CharField(max_length=20, verbose_name=u"验证码")
    email = models.EmailField(max_length=50, verbose_name=u"邮箱")
    send_type = models.CharField(verbose_name=u"验证码类型", choices=(("register", "注册"),("forget", "找回密码"), ("update_email", "修改邮箱")), max_length=30)
    send_time = models.DateTimeField(verbose_name=u"发送时间", default=datetime.now)

    class Meta:
        verbose_name = u"邮箱验证码"
        verbose_name_plural = verbose_name

    def __srt__(self):
        return '{0}({1})'.format(self.code, self.email)
