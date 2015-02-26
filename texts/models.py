from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from moderation.models import TextCoupleCopy


class TextCouple(models.Model):
    short = models.CharField(max_length=30)
    long = models.TextField(max_length=140)
    user = models.ForeignKey(User)

    def __str__(self):
        return '{short} ({long}...)'.format(short=self.short, long=self.long[:7])

    def create_copy(self):
        if not TextCoupleCopy.objects.filter(short=self.short, long=self.long, parent=self.id, user=self.user):
            copy = TextCoupleCopy.objects.create(short=self.short, long=self.long, parent=self.id, user=self.user)
            copy.save()
            return copy
        return None
