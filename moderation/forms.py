from django import forms


STATUSES = (u'Approval pending', u'Accepted', u'Denied', u'Canceled')


class Moderation(forms.Form):
    status = forms.ChoiceField(label='Status:', choices=STATUSES)
    message_from_moderator = forms.Textarea
