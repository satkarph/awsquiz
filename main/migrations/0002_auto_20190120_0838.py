# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-01-20 08:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='durationtime',
            field=models.TimeField(blank=True, default=None, verbose_name='Conversation Time'),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='sub_category',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.SubCategory', verbose_name='Sub-Category'),
        ),
    ]
