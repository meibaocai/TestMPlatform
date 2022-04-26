# Generated by Django 2.2.4 on 2020-11-16 17:21

import datetime
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('manager', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApiCaseInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('api_name', models.CharField(default='', max_length=50, verbose_name='api接口用例名称')),
                ('api_method', models.CharField(default='', max_length=50, verbose_name='api接口Method')),
                ('belong_project_id', models.CharField(max_length=50, verbose_name='关联项目ID')),
                ('designer', models.CharField(default='', max_length=50, verbose_name='设计者')),
                ('modifier', models.CharField(default='', max_length=50, verbose_name='修改者')),
                ('type', models.CharField(choices=[('0', '前后置操作'), ('1', 'CI'), ('2', '非CI'), ('3', '删除')], default='1', max_length=10, verbose_name='用例类型')),
                ('pre_operation', models.CharField(default='', max_length=50, verbose_name='前置操作')),
                ('run_after_operation', models.CharField(default='', max_length=100, verbose_name='执行后操作')),
                ('after_operation', models.CharField(default='', max_length=50, verbose_name='后置操作')),
                ('api_request', models.TextField(verbose_name='请求信息')),
                ('add_time', models.DateTimeField(default=datetime.datetime.now, verbose_name='添加时间')),
                ('update_time', models.DateTimeField(default=datetime.datetime.now, verbose_name='修改时间')),
            ],
            options={
                'verbose_name': 'api用例',
                'verbose_name_plural': 'api用例',
            },
        ),
        migrations.CreateModel(
            name='EnvInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('env_name', models.CharField(default='', max_length=20, verbose_name='环境名称')),
                ('base_url', models.CharField(max_length=50, verbose_name='base_url')),
                ('desc', models.CharField(default='', max_length=50, verbose_name='环境描述')),
                ('add_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='添加时间')),
                ('belong_project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manager.ProjectInfo', verbose_name='所属项目')),
            ],
            options={
                'verbose_name': 'API环境',
                'verbose_name_plural': 'API环境',
            },
        ),
        migrations.CreateModel(
            name='RunApiPlanInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=100, verbose_name='API执行计划名称')),
                ('run_batch', models.CharField(default='', max_length=50, verbose_name='运行批次号')),
                ('belong_project_id', models.CharField(max_length=50, verbose_name='关联项目ID')),
                ('run_user', models.CharField(default='', max_length=50, verbose_name='执行者')),
                ('case_num', models.IntegerField(blank=True, default=None, null=True, verbose_name='用例总数')),
                ('success_num', models.IntegerField(blank=True, default=None, null=True, verbose_name='成功数')),
                ('fail_num', models.IntegerField(blank=True, default=None, null=True, verbose_name='失败数')),
                ('success_ratio', models.FloatField(blank=True, default=None, null=True, verbose_name='成功率')),
                ('start_time', models.DateTimeField(default=datetime.datetime.now, verbose_name='开始时间')),
                ('end_time', models.DateTimeField(default=datetime.datetime.now, verbose_name='结束时间')),
            ],
        ),
        migrations.CreateModel(
            name='RunApiResultInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('api_name', models.CharField(default='', max_length=50, verbose_name='API执行记录名称')),
                ('type', models.CharField(choices=[('1', '单个'), ('2', '批量')], default='1', max_length=10, verbose_name='类型')),
                ('run_batch', models.CharField(default='', max_length=50, verbose_name='运行批次号')),
                ('belong_project_id', models.CharField(max_length=50, verbose_name='关联项目ID')),
                ('file_path', models.FileField(upload_to='api/logs/')),
                ('detail', models.TextField(verbose_name='执行详情')),
                ('status', models.CharField(choices=[('0', '失败'), ('1', '成功')], default='1', max_length=10, verbose_name='执行状态')),
                ('start_time', models.DateTimeField(default=datetime.datetime.now, verbose_name='开始时间')),
                ('end_time', models.DateTimeField(default=datetime.datetime.now, verbose_name='结束时间')),
                ('belong_env', models.ForeignKey(db_constraint=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.EnvInfo', verbose_name='关联环境ID')),
                ('belong_service', models.ForeignKey(db_constraint=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to='manager.ServiceInfo', verbose_name='所属服务')),
                ('related_case', models.ForeignKey(db_constraint=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.ApiCaseInfo', verbose_name='关联用例ID')),
            ],
        ),
        migrations.CreateModel(
            name='OperationInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=50, verbose_name='操作名称')),
                ('belong_project_id', models.CharField(default='', max_length=10, verbose_name='关联项目ID')),
                ('designer', models.CharField(default='', max_length=50, verbose_name='设计者')),
                ('modifier', models.CharField(default='', max_length=50, verbose_name='修改者')),
                ('type', models.CharField(choices=[('0', '用例'), ('1', 'SQL'), ('2', '等待')], default='0', max_length=10, verbose_name='操作类型')),
                ('operation', models.TextField(verbose_name='请求信息')),
                ('status', models.CharField(choices=[('0', '删除'), ('1', '正常')], default='1', max_length=5, verbose_name='用例状态')),
                ('desc', models.CharField(default='', max_length=100, verbose_name='环境描述')),
                ('add_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='添加时间')),
                ('update_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='修改时间')),
                ('belong_env', models.ForeignKey(db_constraint=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.EnvInfo', verbose_name='关联环境ID')),
                ('related_case', models.ForeignKey(db_constraint=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.ApiCaseInfo', verbose_name='关联用例ID')),
            ],
            options={
                'verbose_name': '前后置操作',
                'verbose_name_plural': '前后置操作',
            },
        ),
        migrations.CreateModel(
            name='LocalParameterInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=50, verbose_name='参数名称')),
                ('value', models.CharField(default='', max_length=100, verbose_name='参数值')),
                ('desc', models.CharField(default='', max_length=50, verbose_name='参数描述')),
                ('belong_project_id', models.CharField(default='', max_length=10, verbose_name='关联项目ID')),
                ('belong_env_id', models.CharField(default='', max_length=10, verbose_name='关联环境ID')),
                ('add_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='添加时间')),
                ('update_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='修改时间')),
                ('belong_case', models.ForeignKey(db_constraint=False, on_delete=django.db.models.deletion.CASCADE, to='api.ApiCaseInfo', verbose_name='所属api用例')),
            ],
            options={
                'verbose_name': '局部参数',
                'verbose_name_plural': '局部参数',
            },
        ),
        migrations.CreateModel(
            name='GlobalParameterInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=50, verbose_name='参数名称')),
                ('param_type', models.CharField(choices=[('1', 'KEY-VALUE类型'), ('2', 'SQL类型'), ('3', '测试用例类型')], default='1', max_length=10, verbose_name='参数类型')),
                ('param_content', models.CharField(default='', max_length=1024, verbose_name='参数内容')),
                ('value', models.CharField(default='', max_length=100, verbose_name='参数值')),
                ('desc', models.CharField(default='', max_length=50, verbose_name='参数描述')),
                ('belong_project_id', models.CharField(default='', max_length=50, verbose_name='关联项目ID')),
                ('add_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='添加时间')),
                ('update_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='修改时间')),
                ('belong_env', models.ForeignKey(db_constraint=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.EnvInfo', verbose_name='关联环境ID')),
                ('related_case', models.ForeignKey(db_constraint=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.ApiCaseInfo', verbose_name='关联用例ID')),
            ],
            options={
                'verbose_name': '全局参数',
                'verbose_name_plural': '全局参数',
            },
        ),
        migrations.AddField(
            model_name='apicaseinfo',
            name='belong_env',
            field=models.ForeignKey(db_constraint=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.EnvInfo', verbose_name='关联环境ID'),
        ),
        migrations.AddField(
            model_name='apicaseinfo',
            name='belong_service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manager.ServiceInfo', verbose_name='所属服务'),
        ),
    ]
