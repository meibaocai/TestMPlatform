# Generated by Django 2.2.4 on 2020-08-05 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('case', '0011_auto_20200727_1139'),
    ]

    operations = [
        migrations.AddField(
            model_name='testcase',
            name='parent_list',
            field=models.CharField(default='', max_length=200, verbose_name='父目集合'),
        ),
        migrations.AddField(
            model_name='versioncase',
            name='parent_list',
            field=models.CharField(default='', max_length=200, verbose_name='父目集合'),
        ),
    ]
