# Generated by Django 3.2.10 on 2022-10-10 15:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('interfacetestplatform', '0014_alter_role_title'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userinfo',
            name='depart',
        ),
        migrations.RemoveField(
            model_name='userinfo',
            name='roles',
        ),
        migrations.DeleteModel(
            name='Department',
        ),
        migrations.DeleteModel(
            name='Role',
        ),
    ]
