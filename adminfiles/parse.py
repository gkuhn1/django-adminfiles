import re

from adminfiles import settings
from adminfiles.models import FileUpload

# Upload references look like: <<< upload-slug : key=val : key2=val2 >>>
# Spaces are optional, key-val opts are optional, can be any number
# extra indirection is for testability
def _get_upload_re():
    start, end = (settings.ADMINFILES_REF_START,
                  settings.ADMINFILES_REF_END)
    if not isinstance(end, list):
        # for compatibility mode
        end = list(end)
    if not isinstance(start, list):
        # for compatibility mode
        start = list(start)
    regex = []
    for s, e in zip(start, end):
        regex.append(re.compile(
            r'%s\s*([\w-]+)((\s*:\s*\w+\s*=\s*.+?)*)\s*%s'
                      % (re.escape(s), re.escape(e))))
    return regex
UPLOAD_RES = _get_upload_re()

def get_uploads(text):
    """
    Return a generator yielding uploads referenced in the given text.
    """
    uploads = []
    for re in UPLOAD_RES:
        for match in re.finditer(text):
            try:
                upload = FileUpload.objects.get(slug=match.group(1))
            except FileUpload.DoesNotExist:
                continue
            yield upload

def substitute_uploads(text, sub_callback):
    """
    Return text with all upload references substituted using
    sub_callback, which must accept an re match object and return the
    replacement string.

    """
    ret = ''
    for re in UPLOAD_RES:
        ret = re.sub(sub_callback, text)
    return ret

def parse_match(match):
    """
    Accept an re match object resulting from an ``UPLOAD_RES`` match
    and return a two-tuple where the first element is the
    corresponding ``FileUpload`` and the second is a dictionary of the
    key=value options.

    If there is no ``FileUpload`` object corresponding to the match,
    the first element of the returned tuple is None.

    """
    try:
        upload = FileUpload.objects.get(slug=match.group(1))
    except FileUpload.DoesNotExist:
        upload = None
    options = parse_options(match.group(2))
    return (upload, options)

def parse_options(s):
    """
    Expects a string in the form "key=val:key2=val2" and returns a
    dictionary.

    """
    options = {}
    for option in s.split(':'):
        if '=' in option:
            key, val = option.split('=')
            options[str(key).strip()] = val.strip()
    return options
