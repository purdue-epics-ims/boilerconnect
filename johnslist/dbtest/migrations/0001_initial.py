# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128, verbose_name=b'Job Name')),
                ('description', models.TextField(verbose_name=b'Job Description')),
                ('duedate', models.DateTimeField(verbose_name=b'Date Due')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64, verbose_name=b'Organization Name')),
                ('description', models.TextField(verbose_name=b'Organization Description')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ServiceCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64, verbose_name=b'Service Category Name')),
                ('description', models.TextField(verbose_name=b'Service Category Description')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64, verbose_name=b'Username')),
                ('password', models.CharField(max_length=64, verbose_name=b'Password')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='organization',
            name='admin',
            field=models.ForeignKey(related_name=b'admin', to='dbtest.User'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='organization',
            name='categories',
            field=models.ManyToManyField(to='dbtest.ServiceCategory'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='organization',
            name='members',
            field=models.ManyToManyField(related_name=b'members', to='dbtest.User'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='job',
            name='accepted',
            field=models.ManyToManyField(related_name=b'accepted', to='dbtest.Organization'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='job',
            name='creator',
            field=models.ForeignKey(to='dbtest.User'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='job',
            name='requested',
            field=models.ManyToManyField(related_name=b'requested', to='dbtest.Organization'),
            preserve_default=True,
        ),
    ]
