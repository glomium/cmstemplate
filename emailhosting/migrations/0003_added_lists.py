# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-18 12:14
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import emailhosting.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('emailhosting', '0002_account_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='List',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('all_members', models.BooleanField(default=True, help_text='all active members are inside this list')),
                ('only_members', models.BooleanField(default=True, help_text='only members are allowed to join')),
                ('restricted', models.BooleanField(default=True, help_text='only allowed adresses can write messages')),
            ],
        ),
        migrations.CreateModel(
            name='Subscriber',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('can_send', models.BooleanField(default=False, help_text='is allowed to send messages')),
                ('mailinglist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='emailhosting.List')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterField(
            model_name='account',
            name='gname',
            field=models.CharField(default='default', editable=False, help_text='Used to fragment the default user directoryies', max_length=32, null=True, validators=[emailhosting.models.validate_account_groupname], verbose_name='Groupname'),
        ),
        migrations.AddField(
            model_name='address',
            name='mailinglist',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mail_address', to='emailhosting.List'),
        ),
    ]
