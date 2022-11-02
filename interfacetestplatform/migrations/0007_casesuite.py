# Generated by Django 3.2.10 on 2022-08-24 15:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interfacetestplatform', '0006_testcase'),
    ]

    operations = [
        migrations.CreateModel(
            name='CaseSuite',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('suite_desc', models.CharField(blank=True, max_length=100, null=True, verbose_name='用例集合描述')),
                ('if_execute', models.IntegerField(default=0, help_text='0:执行,1:不执行', verbose_name='是否执行')),
                ('test_case_model', models.CharField(blank=True, help_text='data/keyword', max_length=100, null=True, verbose_name='测试执行模块')),
                ('creator', models.CharField(blank=True, max_length=50, null=True)),
                ('create_time', models.DateTimeField(auto_now=True, verbose_name='创建时间')),
            ],
            options={
                'verbose_name': '测试用例集合表',
                'verbose_name_plural': '测试用例集合表',
            },
        ),
    ]
