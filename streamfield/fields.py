import json
from django.db import models
from django.forms.widgets import Widget, MultiWidget
from django.contrib.admin.options import FORMFIELD_FOR_DBFIELD_DEFAULTS
from django.conf import settings
from .base import StreamObject

BLOCK_OPTIONS = getattr(settings, "STREAMFIELD_BLOCK_OPTIONS", {
    "margins": {
        "label": "Отступы",
        "type": "checkbox",
        "default": True
    }
})


class StreamFieldWidget(Widget):
    template_name = 'streamfield/streamfield_widget.html'

    def __init__(self, attrs=None):
        self.model_list = attrs.pop('model_list', [])
        
        model_list_info = {}
        for block in self.model_list:
            as_list = hasattr(block, "as_list") and block.as_list
            options = block.options if hasattr(block, "options") else BLOCK_OPTIONS
            model_list_info[block.__name__] = {
                'model_doc': block._meta.verbose_name,
                'abstract': block._meta.abstract,
                'as_list': 1 if as_list else 0,
                'options': options
            }
        attrs["model_list_info"] = json.dumps(model_list_info)

        super().__init__(attrs)

    def format_value(self, value):
        if value != "" and not isinstance(value, StreamObject):
            value = StreamObject(value, self.model_list)            
        return value

    class Media:
        css = {
            'all': ('streamfield/css/streamfield_widget.css',)
        }
        js = (
            'streamfield/vendor/lodash.min.js',
            'streamfield/vendor/js.cookie.js',
            'streamfield/vendor/vue.js',
            'streamfield/vendor/Sortable.min.js',
            'streamfield/vendor/vuedraggable.umd.min.js',
            'streamfield/vendor/axios.min.js',
            'streamfield/js/streamfield_widget.js',
            )

class StreamField(models.TextField):
    description = "StreamField"

    def __init__(self, *args, **kwargs):
        self.model_list = kwargs.pop('model_list', [])
        kwargs['null'] = True
        kwargs['blank'] = True
        super().__init__(*args, **kwargs)


    def from_db_value(self, value, expression, connection):
        return self.to_python(value)
        
    def to_python(self, value):
        if not value or isinstance(value, StreamObject):
            return value
        return StreamObject(value, self.model_list)

    def formfield(self, **kwargs):
        widget_class = kwargs.get('widget', StreamFieldWidget)
        attrs = {}
        attrs["model_list"] = self.model_list
        defaults = {
            'widget': widget_class(attrs=attrs),
        }
        return super().formfield(**defaults)


FORMFIELD_FOR_DBFIELD_DEFAULTS[StreamField] = {'widget': StreamFieldWidget}
