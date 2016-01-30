# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64, verbose_name=b'Service Category Name')),
                ('description', models.TextField(verbose_name=b'Service Category Description')),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text_comment', models.TextField(verbose_name=b'text_comment')),
            ],
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128, verbose_name=b'Job Name')),
                ('description', models.TextField(max_length=256, verbose_name=b'Job Description')),
                ('deliverable', models.TextField(max_length=256, verbose_name=b'Deliverable')),
                ('duedate', models.DateTimeField(verbose_name=b'Date Due')),
                ('stakeholders', models.TextField(verbose_name=b'Stakeholders')),
                ('tech_specs', models.TextField(verbose_name=b'Technical Specifications', blank=True)),
                ('budget', models.TextField(verbose_name=b'Budget')),
                ('attachments', models.FileField(upload_to=b'job', blank=True)),
                ('categories', models.ManyToManyField(to='dbtest.Category')),
                ('creator', models.ForeignKey(related_name='jobs', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': (('view_job', 'Can view Job'), ('edit_job', 'Can edit Job'), ('is_creator', 'Is a creator of Job')),
            },
        ),
        migrations.CreateModel(
            name='JobRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('accepted', models.NullBooleanField(default=False)),
                ('declined', models.NullBooleanField(default=False)),
                ('completed', models.NullBooleanField(default=False)),
                ('job', models.ForeignKey(related_name='jobrequests', to='dbtest.Job')),
            ],
            options={
                'permissions': (('view_jobrequest', 'Can view JobRequest'), ('edit_jobrequest', 'Can edit JobRequest')),
            },
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(null=True, verbose_name=b'Organization Name')),
                ('description', models.TextField(verbose_name=b'Organization Description')),
                ('email', models.CharField(max_length=64, null=True, verbose_name=b'Organization email')),
                ('phone_number', models.CharField(max_length=64, null=True, verbose_name=b'Organization phone number')),
                ('icon', models.ImageField(null=True, upload_to=b'organization', blank=True)),
                ('available', models.BooleanField(default=True)),
                ('categories', models.ManyToManyField(to='dbtest.Category')),
                ('group', models.OneToOneField(to='auth.Group')),
            ],
            options={
                'permissions': (('view_organization', 'Can view Organization'), ('edit_organization', 'Can edit Organization'), ('is_admin', 'Is an Administrator')),
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(verbose_name=b'Username')),
                ('purdueuser', models.BooleanField(default=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='jobrequest',
            name='organization',
            field=models.ForeignKey(to='dbtest.Organization'),
        ),
        migrations.AddField(
            model_name='job',
            name='organization',
            field=models.ManyToManyField(to='dbtest.Organization', through='dbtest.JobRequest'),
        ),
        migrations.AddField(
            model_name='comment',
            name='jobrequest',
            field=models.ForeignKey(to='dbtest.JobRequest'),
        ),
    ]
