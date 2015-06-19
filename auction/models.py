from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Auction(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    target_user = models.ForeignKey(User)


class Bid(models.Model):
    auction = models.ForeignKey(Auction)
    price = models.IntegerField()

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    winner = models.BooleanField(default=False)
