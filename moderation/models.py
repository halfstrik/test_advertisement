from django.db import models
from django.contrib.auth.models import User


STATUSES = ((1, u'Approval pending'), (2, u'Accepted'), (3, u'Denied'), (4, u'Canceled'))


class RequestForModeration(models.Model):
    advertising = models.CharField(max_length=20)
    date_of_request = models.DateTimeField(auto_now_add=True)
    moderator = models.ForeignKey(User, null=True)
    date_of_last_moderation = models.DateTimeField(auto_now=True)
    message_from_moderator = models.TextField(null=True)
    status = models.CharField(max_length=16, choices=STATUSES)
