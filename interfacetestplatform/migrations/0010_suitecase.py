# Generated by Django 3.2.10 on 2022-08-25 16:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('interfacetestplatform', '0009_alter_casesuite_test_case_model'),
    ]

    operations = [
        migrations.CreateModel(
            name='SuiteCase',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('status', models.IntegerField(default=1, help_text='0：有效，1：无效', verbose_name='是否有效')),
                ('create_time', models.DateTimeField(auto_now=True, verbose_name='创建时间')),
                ('case_suite', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='interfacetestplatform.casesuite', verbose_name='用例集合')),
                ('test_case', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='interfacetestplatform.testcase', verbose_name='测试用例')),
            ],
        ),
    ]
