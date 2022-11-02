# Generated by Django 3.2.10 on 2022-08-17 16:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('interfacetestplatform', '0003_rename_modulw_module'),
    ]

    operations = [
        migrations.CreateModel(
            name='ModuleTest',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50, verbose_name='模块名称')),
                ('test_owner', models.CharField(max_length=20, verbose_name='测试负责人')),
                ('desc', models.CharField(max_length=20, verbose_name='项目描述')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')),
                ('belong_project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='interfacetestplatform.project')),
            ],
            options={
                'verbose_name': '模块信息表',
                'verbose_name_plural': '模块信息表',
            },
        ),
    ]
