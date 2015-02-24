# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RequestForModeration',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('advertising', models.CharField(max_length=20)),
                ('date_of_request', models.DateTimeField(auto_now_add=True)),
                ('date_of_last_moderation', models.DateTimeField(null=True)),
                ('message_from_moderator', models.TextField(null=True)),
                ('status', models.CharField(max_length=16, choices=[('Approval pending', 'Approval pending'), ('Accepted', 'Accepted'), ('Denied', 'Denied'), ('Canceled', 'Canceled')])),
                ('moderator', models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
