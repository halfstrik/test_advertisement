from django import forms


class AudioAdvertisingForm(forms.Form):
    title = forms.CharField(label='Enter title:', max_length=30, min_length=3)
    audio_file = forms.FileField(label='Select audio file:')

    def clean(self):
        cleaned_data = super(AudioAdvertisingForm, self).clean()
        title = cleaned_data.get("title")
        audio_file = cleaned_data.get("audio_file")
        if (audio_file is None) or (title == ''):
            msg = u"This field is required"
            self.add_error('audio_file', msg)
        else:
            extension = audio_file.name[-4:]
            if extension != '.ogg':
                msg = u"The file must be .ogg extension"
                self.add_error('audio_file', msg)
