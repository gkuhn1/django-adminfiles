import posixpath

from django.http import HttpResponse
from django.contrib import admin
from django.contrib.admin.filters import FieldListFilter
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext_lazy as _

from adminfiles.models import FileUpload, FileUploadReference
try:
    from adminfiles.models import FileGallery, GalleryGeneric
except ImportError:
    FileGallery = None
from adminfiles import settings
from adminfiles.listeners import register_listeners
from adminfiles.widgets import FilePickerWrapper
from adminfiles.forms import FileUploadForm

from adminfiles.views import get_enabled_browsers

from django.utils.datastructures import SortedDict

class ContentTypeListFilter(FieldListFilter):
    title = _(u'type')

    def __init__(self, field, request, params, model, model_admin,
                field_path):
        self.lookup_kwarg = 'c_type'
        self.lookup_val = params.pop(self.lookup_kwarg, None)
        browsers = get_enabled_browsers()
        browsers = sorted(browsers, key=lambda b: b.link_text)
        self._browsers = SortedDict([(b.content_type, b) for b in \
            browsers if b.content_type])

    def expected_parameters(self):
        return [self.lookup_kwarg,]
    def choices(self, cl):
        yield {
            'selected': self.lookup_val is None,
            'query_string': cl.get_query_string({}, [self.lookup_kwarg]),
            'display': _(u'All'),
        }
        for ct, b in self._browsers.items():
            if b.content_type and not b.content_type == 'all':
                yield {
                    'selected': self.lookup_val == ct,
                    'query_string': cl.get_query_string({
                            self.lookup_kwarg: ct,
                        }, [self.lookup_kwarg,]),
                    'display': b.link_text,
                    }

    def queryset(self, request, queryset):
        content_type = self.lookup_val
        if content_type in self._browsers:
            browser = self._browsers.get(content_type)
            query = browser.get_query()
            if isinstance(query, dict):
                queryset = queryset.filter(**query)
            else:
                queryset = queryset.filter(*query)
        return queryset

BaseFileUploadAdmin = admin.ModelAdmin
if settings.ADMINFILES_ALLOW_MULTIUPLOAD:
    from multiupload.admin import MultiUploadAdmin

    class BaseFileUploadAdmin(MultiUploadAdmin):
        multiupload_form = False
        multiupload_maxfilesize = 10 * 2 ** 20 # 10 Mb
        multiupload_minfilesize = 0
        # tuple with mimetype accepted
        multiupload_acceptedformats = (
            # images
            "image/jpeg", "image/pjpeg", "image/png", "image/gif",
            # pdf
            "application/pdf",
            # text
            "text/plain", "application/xml", "text/xml", "text/html",
            # audio
            "audio/mpeg3", "audio/ogg", "audio/wav", "audio/mpeg",
            "audio/mp3",
            # excel files
            "application/excel", "application/vnd.ms-excel",
            "application/x-excel", "application/x-msexcel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            # ppt files
            "application/vnd.ms-powerpoint", "application/mspowerpoint",
            "application/powerpoint", "application/vnd.ms-powerpoint",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation", # pptx
            "application/vnd.openxmlformats-officedocument.presentationml.slideshow", #ppsx
            "application/x-mspowerpoint",
            # doc files
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )

        def process_uploaded_file(self, uploaded, object, request):
            title = request.POST.get('title', '') or uploaded.name
            f = self.model(upload=uploaded, title=title,
                uploaded_by=request.user)
            f.save()
            return {
                'url': f.image_thumb(),
                'thumbnail_url': f.image_thumb(),
                'id': f.id,
                'name': f.title
            }


if FileGallery:
    class FileGalleryInline(generic.GenericTabularInline):
        model = GalleryGeneric
        raw_id_fields = ['gallery',]
        extra = 0

    class FileGalleryAdmin(admin.ModelAdmin):
        # raw_id_fields = ('files',)
        filter_horizontal = ['files']
        prepopulated_fields = {'slug': ('title',)}
        date_hierarchy = 'created_at'
        list_display = ['title', 'description', 'created_at']
        search_fields = ['title', 'description']
    admin.site.register(FileGallery, FileGalleryAdmin)


class FileUploadAdmin(BaseFileUploadAdmin):
    form = FileUploadForm
    list_display = ['admin_image_thumb', 'description',
        'upload_date', 'type']
    list_filter = [('content_type', ContentTypeListFilter), 'uploaded_by']
    date_hierarchy = 'upload_date'
    search_fields = ['title', 'description']
    list_editable = ['description']
    prepopulated_fields = {'slug': ('title',)}
# uncomment for snipshot photo editing feature
#    class Media:
#        js = (JQUERY_URL, posixpath.join(ADMINFILES_STATIC_URL,
#                                         'photo-edit.js'))

    def save_model(self, request, obj, form, change):
        # auto fill uploaded_by with logger user
        obj.uploaded_by = request.user
        super(FileUploadAdmin, self).save_model(request, obj, form, change)

    def response_change(self, request, obj):
        if request.POST.has_key("_popup"):
            return HttpResponse('<script type="text/javascript">'
                                'opener.dismissEditPopup(window);'
                                '</script>')
        return super(FileUploadAdmin, self).response_change(request, obj)

    def delete_view(self, request, *args, **kwargs):
        response = super(FileUploadAdmin, self).delete_view(request,
                                                            *args,
                                                            **kwargs)
        if request.POST.has_key("post") and request.GET.has_key("_popup"):
            return HttpResponse('<script type="text/javascript">'
                                'opener.dismissEditPopup(window);'
                                '</script>')
        return response

    def response_add(self, request, *args, **kwargs):
        if request.POST.has_key('_popup'):
            return HttpResponse('<script type="text/javascript">'
                                'opener.dismissAddUploadPopup(window);'
                                '</script>')
        return super(FileUploadAdmin, self).response_add(request,
                                                         *args,
                                                         **kwargs)

class FilePickerAdmin(object):

    adminfiles_fields = []
    wrapper_class = FilePickerWrapper

    def __init__(self, *args, **kwargs):
        super(FilePickerAdmin, self).__init__(*args, **kwargs)
        register_listeners(self.model, self.adminfiles_fields)

    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super(FilePickerAdmin, self).formfield_for_dbfield(
            db_field, **kwargs)
        if db_field.name in self.adminfiles_fields:

            kwargs = self.get_wrapper_kwargs()
            if isinstance(self.adminfiles_fields, dict):
                kwargs.update(dict(self.adminfiles_fields.get(db_field.name)))

            try:
                wrapper_class = kwargs.pop('wrapper_class')
            except KeyError:
                wrapper_class = self.wrapper_class

            field.widget = wrapper_class(field.widget, **kwargs)
        return field

    def get_wrapper_kwargs(self):
        return {
            'browser_width': settings.ADMINFILES_BROWSER_WIDTH,
            'browser_height': settings.ADMINFILES_BROWSER_HEIGHT,
            'browser_position': settings.ADMINFILES_BROWSER_POSITION,
            'toolbox_position': settings.ADMINFILES_TOOLBOX_POSITION,
        }

    class Media:
        js = (settings.JQUERY_URL.replace(settings.django_settings.STATIC_URL, ''),
              'adminfiles/fancybox/jquery.fancybox-1.3.4.js',
              posixpath.join(settings.ADMINFILES_STATIC_URL, 'adminfiles/model.js'),
              )
        css = {
            'all': (posixpath.join(settings.ADMINFILES_STATIC_URL, 'adminfiles/filepicker.css'),
                'adminfiles/fancybox/jquery.fancybox-1.3.4.css',
                )
        }

admin.site.register(FileUpload, FileUploadAdmin)

class FileUploadInline(generic.GenericTabularInline):
    model = FileUploadReference
    raw_id_fields = ['upload',]
    extra = 0
