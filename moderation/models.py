from django.db import models
from django.contrib.auth.models import User
from texts.models import TextCouple
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


STATUSES = ((1, u'Approval pending'), (2, u'Accepted'), (3, u'Denied'), (4, u'Canceled'))


class RequestForModeration(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    date_of_request = models.DateTimeField(auto_now_add=True)
    moderator = models.ForeignKey(User, null=True)
    date_of_last_moderation = models.DateTimeField(auto_now=True)
    message_from_moderator = models.TextField(null=True)
    status = models.CharField(max_length=16, choices=STATUSES)


class Advertising(models.Model):
    user = models.ForeignKey(User)

    class Meta:
        abstract = True

    def create_copy(self, advertising):
        pass


class TextCoupleCopyManager(models.Manager):
    def create_copy(self, advertising):
        text_couple_copy = self.create(short=advertising.short,
                                       long=advertising.long,
                                       parent_text_couple=advertising,
                                       user=advertising.user)
        return text_couple_copy


class TextCoupleCopy(Advertising):
    short = models.CharField(max_length=30)
    long = models.CharField(max_length=140)
    parent_text_couple = models.ForeignKey(TextCouple)

    objects = TextCoupleCopyManager()

