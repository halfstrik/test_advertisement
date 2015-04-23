from django.db import models
from django.contrib.auth.models import User


class AudioAdvertising(models.Model):
    title = models.CharField(max_length=30)
    audio_file = models.FileField(upload_to='audio_files')
    advertiser = models.ForeignKey(User)

    def __str__(self):
        return '%s %s' % (self.title, self.audio_file.name)