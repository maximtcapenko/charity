from django import forms
from django.utils.safestring import mark_safe

class ImagePreviewWidget(forms.ClearableFileInput):
    template_name = 'django/forms/widgets/input.html'

    def __init__(self, *args, **kwargs):
        self.accept = kwargs.pop('accept', 'image/*')
        super().__init__(*args, **kwargs)

    def render(self, name, value, attrs=None, renderer=None):
        attrs = attrs or {}
        if 'id' not in attrs:
            attrs['id'] = f'id_{name}'
        
        attrs['accept'] = self.accept
            
        preview_id = f'preview_{attrs["id"]}'
        
        output = forms.FileInput.render(self, name, value, attrs, renderer)
        existing_url = value.url if value and hasattr(value, 'url') else '#'
        display_style = 'block' if existing_url != '#' else 'none'
        
        img_html = f'<img id="{preview_id}" src="{existing_url}" class="img-thumbnail mb-2" style="max-height: 200px; display: {display_style};">'

        script = f"""
        <script>
            (function() {{
                const input = document.getElementById('{attrs["id"]}');
                const preview = document.getElementById('{preview_id}');
                const originalUrl = '{existing_url}';
                const accept = '{self.accept}';
                
                function isAccepted(file, accept) {{
                    if (!accept || accept === '*') return true;
                    const acceptedTypes = accept.split(',').map(t => t.trim());
                    for (const type of acceptedTypes) {{
                        if (type.startsWith('.')) {{
                            if (file.name.toLowerCase().endsWith(type.toLowerCase())) return true;
                        }} else if (type.endsWith('/*')) {{
                            const baseType = type.replace('/*', '');
                            if (file.type.startsWith(baseType)) return true;
                        }} else {{
                            if (file.type === type) return true;
                        }}
                    }}
                    return false;
                }}

                input.onchange = function (evt) {{
                    const [file] = this.files;
                    if (file) {{
                        if (!isAccepted(file, accept)) {{
                            alert('This file type is not allowed. Please select: ' + accept);
                            this.value = '';
                            preview.style.display = 'none';
                            return;
                        }}
                        preview.src = URL.createObjectURL(file);
                        preview.style.display = 'block';
                    }} else {{
                        if (originalUrl !== '#') {{
                            preview.src = originalUrl;
                            preview.style.display = 'block';
                        }} else {{
                            preview.style.display = 'none';
                        }}
                    }}
                }};
            }})();
        </script>
        """
        
        return mark_safe(f'<div class="image-preview-container">{img_html}{output}</div>{script}')


class DateRangeWidget(forms.TextInput):
    template_name = 'widgets/daterange_input.html'

    def __init__(self, date_format=None, attrs=None):
        default_attrs = {
            'class': 'form-control daterange-picker',
            'placeholder': 'Select date range...',
            'autocomplete': 'off',
        }
        self.date_format = date_format

        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget'].update({
            'date_format': self.date_format
        })

        return context

    class Media:
        js = ('https://cdn.jsdelivr.net/npm/litepicker/dist/litepicker.js',)
        css = {
            'all': ('https://cdn.jsdelivr.net/npm/litepicker/dist/css/litepicker.css',)
        }


class CoverSelectWidget(forms.Select):
    template_name = 'widgets/cover_select.html'

    def __init__(self, image_func=None, *args, **kwargs):
        self.image_func = image_func
        super().__init__(*args, **kwargs)

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if value and self.image_func:
            obj = option['value'].instance
            option['attrs']['data_src'] = self.image_func(obj)
        return option

    class Media:
        css = {'all': ('https://cdn.jsdelivr.net/npm/tom-select@2.2.2/dist/css/tom-select.bootstrap5.min.css',)}
        js = ('https://cdn.jsdelivr.net/npm/tom-select@2.2.2/dist/js/tom-select.complete.min.js',)
