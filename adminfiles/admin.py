from django.contrib.admin.options import BaseModelAdmin
import posixpath

from django.http import HttpResponse
from django.contrib import admin

from adminfiles.models import FileUpload
from adminfiles import settings
from adminfiles.listeners import register_listeners
from adminfiles.widgets import FilePickerWrapper


class FileUploadAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'upload_date', 'upload', 'mime_type']
    list_editable = ['description']
    prepopulated_fields = {'slug': ('title',)}
# uncomment for snipshot photo editing feature
#    class Media:
#        js = (JQUERY_URL, posixpath.join(ADMINFILES_STATIC_URL,
#                                         'photo-edit.js'))
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
        js = [settings.JQUERY_URL, posixpath.join(settings.ADMINFILES_STATIC_URL, 'adminfiles/model.js')]
        css = {
            'all': (posixpath.join(settings.ADMINFILES_STATIC_URL, 'adminfiles/filepicker.css'), )
        }

admin.site.register(FileUpload, FileUploadAdmin)
