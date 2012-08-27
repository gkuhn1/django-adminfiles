# encoding: utf-8
"""
Thumbnail generation functions
"""

import re

def youtube_thumbnail(instance):
    link = instance.link
    rex = r'(^http(s){0,1}://){0,1}(youtu.be/|(www.){0,1}youtube.com/watch\?v=)(?P<video_id>\w+)'
    match = re.match(rex, link).groupdict()
    video_id = match['video_id']
    url = 'http://i4.ytimg.com/vi/%s/default.jpg'
    return url % video_id

from adminfiles.models import _thumb_functions
def register_thumb_fn(func, contenttype):
    '''
    Decorator to register a new thumb generate function.
    Thumbfunction must return an IMAGE URL.
    Please see youtube_thumbnail for referance
    Usage:
        register_thumb_fn(func, 'content_type_name')
        # register must be in models.py or __init__.py file.
    '''
    global _thumb_functions
    _thumb_functions[contenttype] = func
    return True




