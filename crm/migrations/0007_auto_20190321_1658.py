# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2019-03-21 08:58
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0006_auto_20190317_0114'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Menu',
            new_name='Menus',
        ),
    ]