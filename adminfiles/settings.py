import posixpath

import django
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

django_settings = settings

JQUERY_URL = getattr(settings, 'JQUERY_URL',
                     'http://ajax.googleapis.com/ajax/libs/jquery/1.4/jquery.min.js')

if JQUERY_URL and not ((':' in JQUERY_URL) or (JQUERY_URL.startswith('/'))):
    JQUERY_URL = posixpath.join(settings.STATIC_URL, JQUERY_URL)

# compatibility settings
ADMINFILES_STATIC_URL = getattr(settings, 'ADMINFILES_STATIC_URL',
                               None) or \
                        getattr(settings, 'ADMINFILES_MEDIA_URL',
                               settings.STATIC_URL)
ADMINFILES_MEDIA_URL = ADMINFILES_STATIC_URL

ADMINFILES_UPLOAD_TO = getattr(settings, 'ADMINFILES_UPLOAD_TO',
                              'adminfiles')

ADMINFILES_THUMB_ORDER = getattr(settings, 'ADMINFILES_THUMB_ORDER',
                                 ('-upload_date',))

ADMINFILES_USE_SIGNALS = getattr(settings, 'ADMINFILES_USE_SIGNALS', False)

ADMINFILES_REF_START = getattr(settings, 'ADMINFILES_REF_START', '<<<!')

ADMINFILES_REF_END = getattr(settings, 'ADMINFILES_REF_END', '!>>>')

ADMINFILES_STRING_IF_NOT_FOUND = getattr(settings,
                                         'ADMINFILES_STRING_IF_NOT_FOUND',
                                         u'')

ADMINFILES_INSERT_LINKS = getattr(
    settings,
    'ADMINFILES_INSERT_LINKS',
    {'': [(_('Insert Link'), {})],
     'image': [(_('Insert'), {}),
               (_('Insert (align left)'), {'class': 'left'}),
               (_('Insert (align right)'), {'class': 'right'})]
     },
    )

ADMINFILES_STDICON_SET = getattr(settings, 'ADMINFILES_STDICON_SET', 'nuvola')

ADMINFILES_BROWSER_VIEWS = getattr(settings, 'ADMINFILES_BROWSER_VIEWS',
                                   ['adminfiles.views.AllView',
                                    'adminfiles.views.ImagesView',
                                    'adminfiles.views.AudioView',
                                    'adminfiles.views.FilesView',
                                    'adminfiles.views.FlickrView',
                                    'adminfiles.views.YouTubeView',
                                    'adminfiles.views.YouTubeLinkView',
                                    'adminfiles.views.VimeoView'])

# list with regex to use with links
ADMINFILES_ALLOWED_LINKS = getattr(settings, 'ADMINFILES_ALLOWED_LINKS', [
            (r'(^http(s){0,1}://){0,1}(youtu.be/|(www.){0,1}youtube.com/watch\?v=)\w+', 'youtubelink'),
                                ])


ADMINFILES_BROWSER_WIDTH = getattr(settings, 'ADMINFILES_BROWSER_WIDTH', 400)

ADMINFILES_BROWSER_HEIGHT = getattr(settings, 'ADMINFILES_BROWSER_HEIGHT', 400)

ADMINFILES_BROWSER_POSITION = getattr(settings, 'ADMINFILES_BROWSER_HEIGHT', 'left')

ADMINFILES_TOOLBOX_POSITION = getattr(settings, 'ADMINFILES_BROWSER_HEIGHT', 'bottom')
