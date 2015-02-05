from django.db import models


class TextCouple(models.Model):
    short = models.CharField(max_length=30)
    long = models.CharField(max_length=140)

    def __str__(self):
        return '{short} ({long}...)'.format(short=self.short, long=self.long[:7])
