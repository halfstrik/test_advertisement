from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class RequestForModeration(models.Model):
    APPROVAL_PENDING = 'AP'
    ACCEPTED = 'AC'
    DENIED = 'DE'
    CANCELED = 'CA'
    IS_MODERATED = 'MO'
    STATUS_CHOISES = ((APPROVAL_PENDING, u'Approval pending'), (ACCEPTED, u'Accepted'), (DENIED, u'Denied'),
                      (CANCELED, u'Canceled'), (IS_MODERATED, u'Is moderated'))
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    date_of_request = models.DateTimeField(auto_now_add=True)
    moderator = models.ForeignKey(User, null=True, blank=True)
    date_of_last_moderation = models.DateTimeField(auto_now=True)
    message_from_moderator = models.TextField(max_length=500, null=True, blank=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOISES)
