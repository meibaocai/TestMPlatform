# Generated by Django 2.0 on 2020-01-07 16:05

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('bugs', '0003_auto_20191215_1919'),
    ]

    operations = [
        migrations.AddField(
            model_name='buginfo',
            name='designer',
            field=models.CharField(default='', max_length=50, verbose_name='设计者'),
        ),
        migrations.AddField(
            model_name='buginfo',
            name='modifier',
            field=models.CharField(default='', max_length=50, verbose_name='修改者'),
        ),
        migrations.AlterField(
            model_name='buginfo',
            name='add_time',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='添加时间'),
        ),
        migrations.AlterField(
            model_name='buginfo',
            name='update_time',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='修改时间'),
        ),
    ]
