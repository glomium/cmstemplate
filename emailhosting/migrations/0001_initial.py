# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import emailhosting.models
from emailhosting.utils import RoundcubeMigration


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        RoundcubeMigration('initial'),
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(db_index=True, max_length=64, null=True, unique=True, validators=[emailhosting.models.validate_account_username], verbose_name='Username')),
                ('password', models.CharField(blank=True, db_index=True, max_length=64, null=True, validators=[emailhosting.models.validate_account_password], verbose_name='Password')),
                ('quota', models.PositiveIntegerField(default=0, help_text='A value of 0 means unlimited', verbose_name='Quota in MB')),
                ('uid', models.CharField(default='vmail', help_text='Sets the user under wich the delivery process runs', max_length=32, null=True, verbose_name='User ID')),
                ('gid', models.CharField(default='vmail', help_text='Sets the group under wich the delivery process runs', max_length=32, null=True, verbose_name='Group ID')),
                ('gname', models.CharField(default='vmail', editable=False, help_text='Used to fragment the default user directoryies', max_length=32, null=True, validators=[emailhosting.models.validate_account_groupname], verbose_name='Groupname')),
                ('home', models.CharField(blank=True, help_text='Imap-directory for the user. Renaming does not move the old directory!', max_length=200, null=True, verbose_name='Directory')),
                ('active', models.BooleanField(db_index=True, default=True, verbose_name='Is active')),
            ],
            options={
                'verbose_name': 'Account',
                'permissions': (('list_passwords', 'Lists passwords in AdminView'),),
                'verbose_name_plural': 'Accounts',
            },
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('local', models.CharField(blank=True, help_text='Use blank to catch all', max_length=100, null=True, validators=[emailhosting.models.validate_address_local], verbose_name='Local')),
                ('forward', models.TextField(blank=True, null=True, validators=[emailhosting.models.validate_address_forward], verbose_name='Forward')),
                ('catchall', models.BooleanField(default=False, editable=False)),
                ('standard', models.BooleanField(default=False)),
                ('account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mail_address', to='emailhosting.Account')),
            ],
            options={
                'verbose_name': 'Address',
                'verbose_name_plural': 'Address',
            },
        ),
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subdomain', models.CharField(blank=True, max_length=100, null=True, verbose_name='Subdomain')),
                ('name', models.CharField(max_length=100, null=True, verbose_name='Domainname')),
                ('tld', models.CharField(max_length=10, null=True, verbose_name='Top-Level-Domain')),
                ('full_name', models.CharField(editable=False, max_length=255, null=True, verbose_name='Domainname')),
                ('accept_mail', models.BooleanField(default=True, verbose_name='Accept Emails')),
            ],
            options={
                'verbose_name': 'Domain',
                'verbose_name_plural': 'Domains',
            },
        ),
        migrations.AlterUniqueTogether(
            name='domain',
            unique_together=set([('subdomain', 'name', 'tld')]),
        ),
        migrations.AddField(
            model_name='address',
            name='domain',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mail_address', to='emailhosting.Domain'),
        ),
        migrations.AlterUniqueTogether(
            name='address',
            unique_together=set([('local', 'domain')]),
        ),
    ]
