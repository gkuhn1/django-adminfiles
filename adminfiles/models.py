import os
import mimetypes

from django.conf import settings as django_settings
from django.db import models
from django.template.defaultfilters import slugify
from django.core.files.images import get_image_dimensions
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from sorl.thumbnail import get_thumbnail

from adminfiles import settings

_thumb_functions = {}

if 'tagging' in django_settings.INSTALLED_APPS:
    from tagging.fields import TagField
else:
    TagField = None

class FileUpload(models.Model):
    upload_date = models.DateTimeField(_('upload date'), auto_now_add=True)
    upload = models.FileField(_('file'), upload_to=settings.ADMINFILES_UPLOAD_TO, blank=True, null=True)
    title = models.CharField(_('title'), max_length=100)
    slug = models.SlugField(_('slug'), max_length=100, unique=True)
    link = models.URLField(_('link'), max_length=500, null=True, blank=True)
    description = models.CharField(_('description'), blank=True, max_length=200)
    content_type = models.CharField(editable=False, max_length=100)
    sub_type = models.CharField(editable=False, max_length=100)

    if TagField:
        tags = TagField(_('tags'))
    
    class Meta:
        ordering = ['upload_date', 'title']
        verbose_name = _('file upload')
        verbose_name_plural = _('file uploads')

    def __unicode__(self):
        return self.title

    def clean(self):
        if not self.upload and not self.link:
            # must have a file uploaded or a link
            raise ValidationError(_('You must provide a file or a link.'))

    def mime_type(self):
        return '%s/%s' % (self.content_type, self.sub_type)
    mime_type.short_description = _('mime type')

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

    def image_thumb(self):
        if self.upload and self.is_image():
            return get_thumbnail(self.upload, "144x150").url
        return self.mime_image()

    def mime_image(self):
        global _thumb_functions
        if self.content_type in _thumb_functions:
            return _thumb_functions.get(self.content_type)(self)
        if not settings.ADMINFILES_STDICON_SET:
            return None
        return ('http://www.stdicon.com/%s/%s?size=64'
                % (settings.ADMINFILES_STDICON_SET, self.mime_type()))



class FileUploadReference(models.Model):
    """
    Tracks which ``FileUpload``s are referenced by which content models.

    """
    upload = models.ForeignKey(FileUpload)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = ('upload', 'content_type', 'object_id')
