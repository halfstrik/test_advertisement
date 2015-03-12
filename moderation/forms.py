from django import forms


STATUSES = ((u'Accepted', u'Accepted'), (u'Denied', u'Denied'))


class ModerationForm(forms.Form):
    status = forms.ChoiceField(label='Status:', choices=STATUSES, widget=forms.RadioSelect)
    message_from_moderator = forms.CharField(label='Message', max_length=500, widget=forms.Textarea, required=False)

    def clean(self):
        cleaned_data = super(ModerationForm, self).clean()
        status = cleaned_data.get("status")
        message_from_moderator = cleaned_data.get("message_from_moderator")
        if status == u'Denied' and not message_from_moderator:
            msg = u"If status 'Denied',  then message must be filled."
            self.add_error('message_from_moderator', msg)
