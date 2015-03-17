from django import forms
from moderation.models import RequestForModeration


class ModerationForm(forms.Form):
    status = forms.ChoiceField(label='Status:', choices=RequestForModeration.STATUS_CHOICES[1:3], widget=forms.RadioSelect)
    message_from_moderator = forms.CharField(label='Message', max_length=500, widget=forms.Textarea, required=False)

    def clean(self):
        cleaned_data = super(ModerationForm, self).clean()
        status = cleaned_data.get("status")
        message_from_moderator = cleaned_data.get("message_from_moderator")
        if status == RequestForModeration.DENIED and not message_from_moderator:
            msg = u"If status 'Denied',  then message must be filled."
            self.add_error('message_from_moderator', msg)
