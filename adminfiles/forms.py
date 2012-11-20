# encoding: utf-8
"""
Forms for adminfiles
"""
import re
from django import forms
from django.utils.translation import ugettext as _


from adminfiles import settings
from adminfiles.models import FileUpload

_compiled_regex_list = None

class FileUploadForm(forms.ModelForm):
    class Meta:
        model = FileUpload

    def get_regex(self):
        global _compiled_regex_list
        if _compiled_regex_list:
            return _compiled_regex_list
        _compiled_regex_list = []
        for rex, content_type in settings.ADMINFILES_ALLOWED_LINKS:
            _compiled_regex_list.append((re.compile(rex), content_type))
        return _compiled_regex_list

    def clean_link(self):
        value = self.cleaned_data['link']
        if value:
            # check if link is allowed
            for rex, name in self.get_regex():
                if rex.match(value):
                    self.instance.content_type = name
                    return value
            raise forms.ValidationError(_(u'This link is not allowed.'))



