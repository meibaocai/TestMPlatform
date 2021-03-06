# Generated by Django 2.2.4 on 2020-07-02 10:13

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0029_operationinfo_desc'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apicaseinfo',
            name='type',
            field=models.CharField(choices=[('0', '前后置操作'), ('1', 'CI'), ('2', '非CI'), ('3', '删除')], default='1', max_length=10, verbose_name='用例类型'),
        ),
        migrations.CreateModel(
            name='RunApiResultInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('api_name', models.CharField(default='', max_length=50, verbose_name='API执行记录名称')),
                ('type', models.CharField(choices=[('1', '单个'), ('2', '批量')], default='1', max_length=10, verbose_name='类型')),
                ('belong_project_id', models.CharField(max_length=50, verbose_name='关联项目ID')),
                ('add_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='添加时间')),
                ('file_path', models.FileField(upload_to='api/logs/')),
                ('detail', models.TextField(verbose_name='执行详情')),
                ('belong_env', models.ForeignKey(db_constraint=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.EnvInfo', verbose_name='关联环境ID')),
                ('related_case', models.ForeignKey(db_constraint=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.ApiCaseInfo', verbose_name='关联用例ID')),
            ],
        ),
    ]
