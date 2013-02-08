import os
import re
import mimetypes

from django.conf import settings as django_settings
from django.db import models
from django.db.models import Q
from django.template.defaultfilters import slugify
from django.core.files.images import get_image_dimensions
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User

from sorl.thumbnail import get_thumbnail

from adminfiles import settings

_thumb_functions = {}

if 'tagging' in django_settings.INSTALLED_APPS:
    from tagging.fields import TagField
else:
    TagField = None

class FileQuerysetFilter(object):
    '''
    Filter a file queryset. This was created to encapsulate all
        file filters.
    '''
    def __init__(self, queryset):
        self.files = queryset
    def filter_images(self):
        'return just images files'
        return self.files.filter(content_type='image')
    def filter_audios(self):
        'Return audios'
        return self.files.filter(content_type='audio')
    def filter_videos(self):
        'Return videos and youtubelinks'
        if settings.ADMINFILES_VIDEOS_JUST_YOUTUBE:
            return self.files.filter(Q(content_type='youtubelink'))
        return self.files.filter(Q(content_type='youtubelink')|
            Q(content_type='video'))
    def filter_docs(self):
        'Return files'
        not_files = ['image', 'audio', 'youtubelink']
        if not settings.ADMINFILES_VIDEOS_JUST_YOUTUBE:
            not_files.append('video')
        return self.files.exclude(content_type__in=not_files)

if settings.ADMINFILES_ENABLE_GALLERY:
    class FileGallery(models.Model):
        title = models.CharField(_('title'), max_length=100)
        slug = models.SlugField(_('slug'), max_length=100, unique=True)
        description = models.CharField(_('description'), blank=True,
                                        max_length=200)
        created_at = models.DateTimeField(_('created'), auto_now_add=True)
        files = models.ManyToManyField('FileUpload', verbose_name=_(u'Files'))
        class Meta:
            verbose_name = _('file gallery')
            verbose_name_plural = _('file galleries')
            ordering = ['created_at',]
            app_label = settings.ADMINFILES_APP_LABEL
            db_table = 'adminfiles_filegallery'
        def __unicode__(self):
            return self.title
        def filter_images(self):
            'return just images files from this gallery'
            return FileQuerysetFilter(self.files).filter_images()
        def filter_audios(self):
            'Return audios'
            return FileQuerysetFilter(self.files).filter_audios()
        def filter_videos(self):
            'Return videos and youtubelinks'
            return FileQuerysetFilter(self.files).filter_videos()
        def filter_docs(self):
            'Return files'
            return FileQuerysetFilter(self.files).filter_docs()

    class GalleryGeneric(models.Model):
        gallery = models.ForeignKey('FileGallery', verbose_name=_(u'gallery'))
        order = models.IntegerField(_(u'Order'), null=True, blank=True)
        content_type = models.ForeignKey(ContentType)
        object_id = models.PositiveIntegerField()
        content_object = generic.GenericForeignKey('content_type', 'object_id')
        class Meta:
            ordering = ['order', 'id']
            verbose_name = _('gallery')
            verbose_name_plural = _('galleries')
            app_label = settings.ADMINFILES_APP_LABEL
            db_table = 'adminfiles_gallerygeneric'
        def __unicode__(self):
            return self.gallery.title

def file_upload_to(instance, filename):
    path = settings.ADMINFILES_UPLOAD_TO
    try:
        name, ext = filename.rsplit('.', 1)
    except ValueError:
        # when file has no extension
        name = filename
        ext = None
    name = slugify(name).replace('-','_')
    return os.path.join(path, '%s%s%s' % (name, ext and '.' or '',
        ext or ''))

class FileUpload(models.Model):
    upload_date = models.DateTimeField(_('upload date'), auto_now_add=True)
    upload = models.FileField(_('file'), upload_to=file_upload_to,
        blank=True, null=True)
    title = models.CharField(_('title'), max_length=100)
    slug = models.SlugField(_('slug'), max_length=100, unique=True)
    link = models.URLField(_('link'), max_length=500, null=True, blank=True)
    description = models.CharField(_('description'), blank=True, max_length=200)
    content_type = models.CharField(editable=False, max_length=100)
    sub_type = models.CharField(editable=False, max_length=100)
    uploaded_by = models.ForeignKey(User, blank=True, null=True,
        verbose_name=_(u'uploaded by'), related_name='uploaded_files')

    if TagField:
        tags = TagField(_('tags'))
    
    class Meta:
        ordering = settings.ADMINFILES_FILES_DEFAULT_ORDERING
        verbose_name = _('file upload')
        verbose_name_plural = _('file uploads')
        db_table = 'adminfiles_fileupload'

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        if self.upload:
            return self.upload.url
        return self.link

    def clean(self):
        if not self.upload and not self.link:
            # must have a file uploaded or a link
            raise ValidationError(_('You must provide a file or a link.'))

    def mime_type(self):
        return '%s/%s' % (self.content_type, self.sub_type)
    mime_type.short_description = _('mime type')
    def type(self):
        types = {
           'audio': _(u'Audio'),
           'image': _(u'Image'),
           'youtubelink': _(u'youtube link'),
        }
        return types.get(self.content_type, _('file'))
    type.short_description = _('type')

    def type_slug(self):
        return slugify(self.sub_type)

    def is_image(self):
        return self.content_type == 'image'

    def _get_dimensions(self):
        try:
            return self._dimensions_cache
        except AttributeError:
            if self.is_image():
                self._dimensions_cache = get_image_dimensions(self.upload.path)
            else:
                self._dimensions_cache = (None, None)
        return self._dimensions_cache
    
    def width(self):
        return self._get_dimensions()[0]
    
    def height(self):
        return self._get_dimensions()[1]
    
    def save(self, *args, **kwargs):
        if self.upload:
            (mime_type, encoding) = mimetypes.guess_type(self.upload.path)
            try:
                [self.content_type, self.sub_type] = mime_type.split('/')
                if self.content_type == 'application' and \
                    self.sub_type == 'ogg':
                    self.content_type = 'audio'
            except:
                self.content_type = 'text'
                self.sub_type = 'plain'
        else:
            # is link
            # content type was filled in form clean
            assert self.content_type
            self.sub_type = 'link'
        super(FileUpload, self).save()

    def insert_links(self):
        links = []
        for key in [self.mime_type(), self.content_type, '']:
            if key in settings.ADMINFILES_INSERT_LINKS:
                links = settings.ADMINFILES_INSERT_LINKS[key]
                break
        for link in links:
            ref = self.slug
            opts = ':'.join(['%s=%s' % (k,v) for k,v in link[1].items()])
            if opts:
                ref += ':' + opts
            yield {'desc': link[0],
                   'ref': ref}

    def image_thumb(self, admin=False):
        if self.upload and self.is_image():
            size = "144x150"
            if admin:
                size = 'x60'
            try:
                return get_thumbnail(self.upload, size).url
            except IOError, e:
                # if file doesnt exists, fail silently
                return ''
        return self.mime_image()

    def admin_image_thumb(self):
        thumb = ''
        if settings.ADMINFILES_SHOW_THUMB:
            thumb = '<br/><img src="%s" style="max-height: 60px" />' % (
                self.image_thumb(admin=True))
        return '%s%s' % (self.title, thumb)
    admin_image_thumb.allow_tags = True
    admin_image_thumb.admin_order_field = 'title'
    admin_image_thumb.short_description = _(u'Thumbnail')

    def mime_image(self):
        global _thumb_functions
        if self.content_type in _thumb_functions:
            return _thumb_functions.get(self.content_type)(self)
        if not settings.ADMINFILES_STDICON_SET:
            return None
        return ('http://www.stdicon.com/%s/%s?size=64'
                % (settings.ADMINFILES_STDICON_SET, self.mime_type()))

    def youtube_code(self):
        '''
        Parse youtube link to get the code for embeding
        '''
        assert self.content_type == 'youtubelink', _(u'Must be a youtubelink')
        rex = r'(^http(s){0,1}://){0,1}(youtu.be/|(www.){0,1}youtube.com/watch\?v=)(?P<video_id>[\w-]+)'
        match = re.match(rex, self.link).groupdict()
        return match['video_id']



class FileUploadReference(models.Model):
    """
    Tracks which ``FileUpload``s are referenced by which content models.

    """
    upload = models.ForeignKey(FileUpload, verbose_name=_(u'file'))
    order = models.IntegerField(_(u'Order'), null=True,
        default=10)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = ('upload', 'content_type', 'object_id')
        db_table = 'adminfiles_fileuploadreference'
        app_label = settings.ADMINFILES_APP_LABEL
        ordering = ('order', '-id')
        verbose_name = _(u'File')
        verbose_name_plural = _(u'Files')



from django.template.defaultfilters import slugify

def find_available_slug(object, instance, slug):
    """
    Recursive method that will add underscores to a slug field
    until a free value is located
    """
    try:
        sender_node = object.objects.get(slug=slug)
    except object.DoesNotExist:
        instance.slug = slug
    else:
        slug = '%s_' % slug
        find_available_slug(object, instance, slug)
    return

def slug_generator(sender, **kwargs):
    """ Generates a unique slug for a node """
    instance = kwargs['instance']
    if instance.slug is not '':
        return
    slug = slugify(instance.title)
    find_available_slug(sender, instance, slug)
models.signals.pre_save.connect(slug_generator, sender=FileUpload)
