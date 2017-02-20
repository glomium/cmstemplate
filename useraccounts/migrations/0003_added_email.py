# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('useraccounts', '0002_changed_username_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Email',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(unique=True, max_length=254, verbose_name='email address', db_index=True)),
                ('is_primary', models.BooleanField(default=False, db_index=True, verbose_name='primary')),
                ('is_valid', models.BooleanField(default=False, db_index=True, verbose_name='valid')),
                ('validated', models.DateTimeField(verbose_name='validated', null=True, editable=False, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='updated')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Email',
                'verbose_name_plural': 'Emails',
            },
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'verbose_name': 'User', 'verbose_name_plural': 'Users'},
        ),
        migrations.AlterModelManagers(
            name='user',
            managers=[
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='auth_token',
            field=models.CharField(null=True, editable=False, max_length=40, blank=True, unique=True, verbose_name='auth_token'),
        ),
        migrations.AddField(
            model_name='user',
            name='is_valid',
            field=models.BooleanField(default=False, help_text='Designates if the user has a valid email address.', verbose_name='valid'),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(error_messages={'unique': 'A user with that username already exists.'}, max_length=150, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', unique=True, verbose_name='username', db_index=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(verbose_name='email address', max_length=254, editable=False, blank=True),
        ),
        migrations.AddField(
            model_name='email',
            name='user',
            field=models.ForeignKey(related_name='emails', to=settings.AUTH_USER_MODEL),
        ),
    ]
