from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from moderation.models import RequestForModeration


class TextCouple(models.Model):
    short = models.CharField(max_length=30)
    long = models.TextField(max_length=140)
    user = models.ForeignKey(User)

    def __str__(self):
        return '{short} ({long}...)'.format(short=self.short, long=self.long[:7])

    def create_copy(self):
        if not TextCoupleCopy.objects.filter(short=self.short, long=self.long, parent=self, user=self.user):
            copy = TextCoupleCopy.objects.create(short=self.short, long=self.long, parent=self, user=self.user)
            copy.save()
            return copy
        elif not RequestForModeration.objects.filter(content_type=ContentType.objects.get_for_model(TextCoupleCopy),
                                                     object_id=TextCoupleCopy.objects.get(short=self.short,
                                                                                          long=self.long,
                                                                                          parent=self,
                                                                                          user=self.user).id):
            copy = TextCoupleCopy.objects.get(short=self.short, long=self.long, parent=self, user=self.user)
            return copy
        else:
            return None


class TextCoupleCopy(models.Model):
    short = models.CharField(max_length=30)
    long = models.TextField(max_length=140)
    user = models.ForeignKey(User)
    parent = models.ForeignKey(TextCouple, null=True)

    def __str__(self):
        return '{short} ({long}...)'.format(short=self.short, long=self.long[:7])

    def display(self):
        return '{short} \n {long}'.format(short=self.short, long=self.long)

    def canceled_request_for_moderation(self):
        request_for_moderation = RequestForModeration.objects.get(content_type=ContentType.objects.
                                                                  get_for_model(TextCoupleCopy), object_id=self.id)
        request_for_moderation.status = u'Canceled'
        request_for_moderation.message_from_moderator = 'The original has been changed.'
        request_for_moderation.save()
