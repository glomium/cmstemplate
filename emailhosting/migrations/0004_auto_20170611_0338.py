# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-11 01:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('emailhosting', '0003_added_lists'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='list',
            name='all_members',
        ),
        migrations.RemoveField(
            model_name='list',
            name='only_members',
        ),
        migrations.RemoveField(
            model_name='list',
            name='restricted',
        ),
        migrations.AddField(
            model_name='list',
            name='check_sender',
            field=models.BooleanField(default=True, help_text='Check sender email address'),
        ),
        migrations.AddField(
            model_name='list',
            name='from_members',
            field=models.BooleanField(default=True, help_text='All members are allowed to send'),
        ),
        migrations.AddField(
            model_name='list',
            name='is_private',
            field=models.BooleanField(default=True, help_text='Only members can join private lists'),
        ),
        migrations.AddField(
            model_name='list',
            name='to_members',
            field=models.BooleanField(default=True, help_text='Send mail to all members'),
        ),
    ]
