from django.db import models
from django.contrib.auth.models import User


class TextCouple(models.Model):
    short = models.CharField(max_length=30)
    long = models.TextField(max_length=140)
    user = models.ForeignKey(User)

    def __str__(self):
        return '{short} ({long}...)'.format(short=self.short, long=self.long[:7])
