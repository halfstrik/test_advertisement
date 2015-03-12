from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


STATUSES = ((0, u'Approval pending'), (1, u'Accepted'), (2, u'Denied'), (3, u'Canceled'), (4, u'Is moderated'))


class RequestForModeration(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    date_of_request = models.DateTimeField(auto_now_add=True)
    moderator = models.ForeignKey(User, null=True, blank=True)
    date_of_last_moderation = models.DateTimeField(auto_now=True)
    message_from_moderator = models.TextField(max_length=500, null=True, blank=True)
    status = models.CharField(max_length=16, choices=STATUSES)
