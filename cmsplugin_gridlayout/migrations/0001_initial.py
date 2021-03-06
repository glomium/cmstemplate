# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-24 06:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cms', '0016_auto_20160608_1535'),
    ]

    operations = [
        migrations.CreateModel(
            name='Column',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, related_name='cmsplugin_gridlayout_column', serialize=False, to='cms.CMSPlugin')),
                ('xs', models.CharField(blank=True, choices=[('', 'Use default'), ('1', '1 Span'), ('2', '2 Span'), ('3', '3 Span'), ('4', '4 Span'), ('5', '5 Span'), ('6', '6 Span'), ('7', '7 Span'), ('8', '8 Span'), ('9', '9 Span'), ('10', '10 Span'), ('11', '11 Span'), ('12', '12 Span')], default='12', max_length=2, null=True, verbose_name='Phone')),
                ('sm', models.CharField(blank=True, choices=[('', 'Use default'), ('1', '1 Span'), ('2', '2 Span'), ('3', '3 Span'), ('4', '4 Span'), ('5', '5 Span'), ('6', '6 Span'), ('7', '7 Span'), ('8', '8 Span'), ('9', '9 Span'), ('10', '10 Span'), ('11', '11 Span'), ('12', '12 Span')], default='', max_length=2, null=True, verbose_name='Tablet')),
                ('md', models.CharField(blank=True, choices=[('', 'Use default'), ('1', '1 Span'), ('2', '2 Span'), ('3', '3 Span'), ('4', '4 Span'), ('5', '5 Span'), ('6', '6 Span'), ('7', '7 Span'), ('8', '8 Span'), ('9', '9 Span'), ('10', '10 Span'), ('11', '11 Span'), ('12', '12 Span')], default='', max_length=2, null=True, verbose_name='Laptop')),
                ('lg', models.CharField(blank=True, choices=[('', 'Use default'), ('1', '1 Span'), ('2', '2 Span'), ('3', '3 Span'), ('4', '4 Span'), ('5', '5 Span'), ('6', '6 Span'), ('7', '7 Span'), ('8', '8 Span'), ('9', '9 Span'), ('10', '10 Span'), ('11', '11 Span'), ('12', '12 Span')], default='', max_length=2, null=True, verbose_name='Desktop')),
                ('xl', models.CharField(blank=True, choices=[('', 'Use default'), ('1', '1 Span'), ('2', '2 Span'), ('3', '3 Span'), ('4', '4 Span'), ('5', '5 Span'), ('6', '6 Span'), ('7', '7 Span'), ('8', '8 Span'), ('9', '9 Span'), ('10', '10 Span'), ('11', '11 Span'), ('12', '12 Span')], default='', max_length=2, null=True, verbose_name='Large Desktop')),
                ('hidden', models.CharField(blank=True, choices=[('', 'Always visible'), ('hidden-sm-down', 'hidden-sm-down'), ('hidden-sm-up', 'hidden-sm-up'), ('hidden-md-down', 'hidden-md-down'), ('hidden-md-up', 'hidden-md-up'), ('hidden-lg-down', 'hidden-lg-down'), ('hidden-lg-up', 'hidden-lg-up')], default='', max_length=20, null=True, verbose_name='Hide Column')),
                ('css', models.CharField(blank=True, default='', max_length=40, null=True, verbose_name='Additional class')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='Row',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, related_name='cmsplugin_gridlayout_row', serialize=False, to='cms.CMSPlugin')),
                ('css', models.CharField(blank=True, default='', max_length=40, null=True, verbose_name='Additional class')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, related_name='cmsplugin_gridlayout_section', serialize=False, to='cms.CMSPlugin')),
                ('name', models.CharField(blank=True, max_length=200, null=True, verbose_name='Name')),
                ('slug', models.SlugField(blank=True, max_length=200, null=True, verbose_name='Slug')),
                ('container', models.CharField(blank=True, choices=[('c', 'Fixed'), ('f', 'Fluid')], default='c', max_length=1, null=True, verbose_name='Container')),
                ('css', models.CharField(blank=True, max_length=200, null=True, verbose_name='CSS')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
    ]
