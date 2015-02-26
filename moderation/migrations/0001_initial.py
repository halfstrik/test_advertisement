# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('texts', '__first__'),
        ('contenttypes', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RequestForModeration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('date_of_request', models.DateTimeField(auto_now_add=True)),
                ('date_of_last_moderation', models.DateTimeField(auto_now=True)),
                ('message_from_moderator', models.TextField(null=True)),
                ('status', models.CharField(choices=[(1, 'Approval pending'), (2, 'Accepted'), (3, 'Denied'), (4, 'Canceled')], max_length=16)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType', default='1')),
                ('moderator', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TextCoupleCopy',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('short', models.CharField(max_length=30)),
                ('long', models.CharField(max_length=140)),
                ('parent_text_couple', models.ForeignKey(to='texts.TextCouple')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
