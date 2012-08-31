# encoding: utf-8
"""
Thumbnail generation functions
"""

def youtube_thumbnail(instance):
    video_id = instance.youtube_code()
    url = 'http://i4.ytimg.com/vi/%s/default.jpg'
    return url % video_id

from adminfiles.models import _thumb_functions
def register_thumb_fn(func, contenttype):
    '''
    Fn to register a new thumb generate function.
    Thumbfunction must return an IMAGE URL.
    Please see youtube_thumbnail for referance
    Usage:
        register_thumb_fn(func, 'content_type_name')
        # register must be in models.py or __init__.py file.
    '''
    global _thumb_functions
    if contenttype in _thumb_functions:
        raise Exception('%s already registered.' % contenttype)
    _thumb_functions[contenttype] = func
    return True




