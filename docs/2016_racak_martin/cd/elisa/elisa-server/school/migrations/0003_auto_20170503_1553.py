# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-03 13:53
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0002_auto_20170501_1739'),
    ]

    operations = [
        migrations.RenameField(
            model_name='department',
            old_name='abbreviation',
            new_name='abbr',
        ),
        migrations.RenameField(
            model_name='group',
            old_name='abbreviation',
            new_name='abbr',
        ),
    ]
