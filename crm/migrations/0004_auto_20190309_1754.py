# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2019-03-09 09:54
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0003_auto_20190309_1751'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Menu',
        ),
        migrations.RemoveField(
            model_name='role',
            name='menu',
        ),
    ]