# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-28 16:42
from __future__ import unicode_literals

import django.contrib.postgres.fields.ranges
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('school', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', django.contrib.postgres.fields.ranges.IntegerRangeField()),
                ('day', models.PositiveSmallIntegerField(choices=[(1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thursday'), (5, 'Friday'), (6, 'Saturday'), (7, 'Sunday')])),
            ],
        ),
        migrations.CreateModel(
            name='EventCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300)),
            ],
        ),
        migrations.CreateModel(
            name='Timetable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300)),
                ('date_start', models.DateField()),
                ('date_end', models.DateField()),
            ],
        ),
        migrations.AddField(
            model_name='event',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetables.EventCategory'),
        ),
        migrations.AddField(
            model_name='event',
            name='courses',
            field=models.ManyToManyField(to='school.Course'),
        ),
        migrations.AddField(
            model_name='event',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='school.Room'),
        ),
        migrations.AddField(
            model_name='event',
            name='timetable',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetables.Timetable'),
        ),
    ]
