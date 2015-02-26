from django.contrib import admin

from moderation.models import TextCoupleCopy, RequestForModeration


admin.site.register(TextCoupleCopy)
admin.site.register(RequestForModeration)
