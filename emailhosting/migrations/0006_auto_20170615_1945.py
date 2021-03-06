# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-15 17:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('emailhosting', '0005_auto_20170611_1120'),
    ]

    operations = [
        migrations.AlterField(
            model_name='list',
            name='check_sender',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(0, 'Allow all senders'), (1, 'Allow all subscribers'), (2, 'Allow all members'), (3, 'Allow only priviledged subscribers')], default=3, help_text='Check sender email address'),
        ),
        migrations.AlterField(
            model_name='list',
            name='is_public',
            field=models.BooleanField(default=False, help_text='Is the list subscribable from non registered users'),
        ),
        migrations.AlterUniqueTogether(
            name='subscriber',
            unique_together=set([('mailinglist', 'email')]),
        ),
    ]
