from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as __
from django.core.urlresolvers import reverse


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

        self.browser_width = kwargs.get('browser_width')
        self.browser_height = kwargs.get('browser_height')
        self.browser_position = kwargs.get('browser_position')
        self.toolbox_position = kwargs.get('toolbox_position')

        self.component_classes = ['adminfilespicker']
        self.widget_classes = ['adminfilespicker-widget']
        self.wrapper_classes = ['adminfilespicker-wrapper']
        self.toolbox_classes = ['adminfilespicker-toolbox']
        self.browser_classes = ['adminfilespicker-browser']

        if self.toolbox_position == 'left':
            self.widget_classes.append('adminfilespicker-widget-left')
            self.toolbox_classes.append('adminfilespicker-toolbox-left')


        if self.browser_position == 'left':
            self.wrapper_classes.append('adminfilespicker-wrapper-left')
            self.browser_classes.append('adminfilespicker-browser-left')
        elif self.browser_position == 'fixed':
            self.toolbox_classes.append('toolbox-fixed')

        try:
            self.widget.attrs['class'] += ' '+' '.join(self.widget_classes)
        except KeyError:
            self.widget.attrs['class'] = ' '.join(self.widget_classes)


    def render(self, *args, **kwargs):
        widget_output = super(FilePickerWrapper, self).render(*args, **kwargs)
        output = ['<div class="%s">' % ' '.join(self.component_classes),'</div>']

        toolbox_markup = '<div class="%s">\
                            <a class="addlink adminfilespicker-trigger" \
                                href="%s">%s\
                                </a>\
                            </div>' % (
                                ' '.join(self.toolbox_classes),
                                reverse('adminfiles_all'),
                                self.labels['add_file'],
                            )
        browser_markup = '<div class="%s">\
                                <iframe frameborder="0" style="border:none; width:%dpx; height:%dpx;"></iframe>\
                            </div>' % (' '.join(self.browser_classes), self.browser_width, self.browser_height)
        wrapper_markup = '<div class="%s">%s</div>' \
                        % (' '.join(self.wrapper_classes), ''.join([widget_output, toolbox_markup]), )

        output.insert(1, ''.join([wrapper_markup, browser_markup]))
        return mark_safe(''.join(output))

