from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as __


class BaseWidgetWrapper(object):

    overrides = ['render', '__deepcopy__']

    def __init__(self, widget, **kwargs):
        self.widget = widget

    def __getattr__(self, item):
        if item not in self.overrides:
            if not hasattr(self.widget, item):
                raise AttributeError("Widget class '%r' has no attribute '%s'" % (self.widget, item))
            return getattr(self.widget, item)
        else:
            if not hasattr(self, item):
                raise AttributeError("Widget Wrapper class '%r' has no attribute '%s'" % (self, item))

    def render(self, *args, **kwargs):
        return self.widget.render(*args, **kwargs)

    def __deepcopy__(self, memo):
        self.widget = self.widget.__deepcopy__(memo)
        return self


class FilePickerWrapper(BaseWidgetWrapper):

    labels = {
        'add_file': __(u'Add file')
    }

    def __init__(self, widget, **kwargs):
        super(FilePickerWrapper, self).__init__(widget, **kwargs)
        try:
            self.widget.attrs['class'] += ' adminfilespicker'
        except KeyError:
            self.widget.attrs['class'] = 'adminfilespicker'

    def render(self, *args, **kwargs):
        widget_output = super(FilePickerWrapper, self).render(*args, **kwargs)
        output = ['<div class="adminfilespicker-wrapper adminfilespicker-wrapper-bottom">']
        output.append(widget_output)
        output.append('<div class="adminfilespicker-toolbox">')
        output.append('<a class="addlink adminfilespicker-trigger">%s</a>' % self.labels['add_file'])
        output.append('</div></div>')
        return mark_safe(''.join(output))