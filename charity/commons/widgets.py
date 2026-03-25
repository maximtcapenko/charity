from django import forms
from django.utils.safestring import mark_safe

class ImagePreviewWidget(forms.ClearableFileInput):
    def __init__(self, *args, **kwargs):
        self.accept = kwargs.pop('accept', 'image/*')
        super().__init__(*args, **kwargs)

    def render(self, name, value, attrs=None, renderer=None):
        attrs = attrs or {}
        if 'id' not in attrs:
            attrs['id'] = f'id_{name}'
        
        attrs['accept'] = self.accept
            
        preview_id = f'preview_{attrs["id"]}'
        output = super().render(name, value, attrs, renderer)
        
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
