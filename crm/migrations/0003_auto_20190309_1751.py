# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2019-03-09 09:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0002_auto_20190307_0154'),
    ]

    operations = [
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('url_type', models.SmallIntegerField(choices=[(0, 'absolute'), (1, 'dynamic')], default=0)),
                ('url_name', models.CharField(max_length=128)),
            ],
        ),
        migrations.AlterField(
            model_name='role',
            name='name',
            field=models.CharField(max_length=64, unique=True),
        ),
        migrations.AlterUniqueTogether(
            name='menu',
            unique_together=set([('name', 'url_name')]),
        ),
        migrations.AddField(
            model_name='role',
            name='menu',
            field=models.ManyToManyField(blank=True, to='crm.Menu'),
        ),
    ]