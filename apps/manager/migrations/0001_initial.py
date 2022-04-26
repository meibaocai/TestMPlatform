# Generated by Django 2.2.4 on 2020-11-16 17:21

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DepartmentInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=20, verbose_name='部门名称')),
                ('creator', models.CharField(default='admin', max_length=10, verbose_name='创建人')),
                ('add_time', models.DateField(default=datetime.datetime.now, verbose_name='添加时间')),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='my_father', to='manager.DepartmentInfo', verbose_name='上级部门')),
            ],
            options={
                'verbose_name': '公司组织架构信息',
                'verbose_name_plural': '公司组织架构信息',
            },
        ),
        migrations.CreateModel(
            name='ProjectInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_name', models.CharField(default='', max_length=50, verbose_name='项目名称')),
                ('project_desc', models.CharField(default='', max_length=50, verbose_name='项目描述')),
                ('creator', models.CharField(default='admin', max_length=10, verbose_name='创建人')),
                ('status', models.CharField(choices=[('0', '删除'), ('1', '正常')], default='1', max_length=5, verbose_name='项目状态')),
                ('add_time', models.DateField(default=datetime.datetime.now, verbose_name='添加时间')),
                ('blong_department', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='manager.DepartmentInfo', verbose_name='所属部门')),
            ],
            options={
                'verbose_name': '项目信息',
                'verbose_name_plural': '项目信息',
            },
        ),
        migrations.CreateModel(
            name='VersionInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version_name', models.CharField(default='', max_length=50, verbose_name='版本名称')),
                ('version_desc', models.CharField(default='', max_length=100, verbose_name='版本描述')),
                ('creator', models.CharField(default='admin', max_length=10, verbose_name='创建人')),
                ('status', models.CharField(choices=[('0', '删除'), ('1', '正常')], default='1', max_length=5, verbose_name='版本状态')),
                ('add_time', models.DateField(default=datetime.datetime.now, verbose_name='添加时间')),
                ('belong_project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manager.ProjectInfo', verbose_name='所属项目')),
            ],
            options={
                'verbose_name': '版本信息',
                'verbose_name_plural': '版本信息',
            },
        ),
        migrations.CreateModel(
            name='ServiceInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=50, verbose_name='服务名称')),
                ('desc', models.CharField(default='', max_length=100, verbose_name='服务描述')),
                ('creator', models.CharField(default='admin', max_length=10, verbose_name='创建人')),
                ('add_time', models.DateField(default=datetime.datetime.now, verbose_name='添加时间')),
                ('status', models.CharField(choices=[('0', '删除'), ('1', '正常')], default='1', max_length=5, verbose_name='服务状态')),
                ('belong_project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manager.ProjectInfo', verbose_name='所属项目')),
            ],
            options={
                'verbose_name': '服务信息',
                'verbose_name_plural': '服务信息',
            },
        ),
    ]
