from django import forms
from .models import Machine, Evidence, Vulnerability, Exploit, Screenshot, Flag

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class BaseStyledForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                current_class = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = f"form-check-input {current_class}".strip()
            elif isinstance(field.widget, forms.Select):
                current_class = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = f"form-select {current_class}".strip()
            elif isinstance(field.widget, forms.FileInput) or isinstance(field.widget, forms.ClearableFileInput) or isinstance(field.widget, MultipleFileInput):
                current_class = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = f"form-control {current_class}".strip()
            else:
                current_class = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = f"form-control {current_class}".strip()

class MachineForm(BaseStyledForm):
    class Meta:
        model = Machine
        fields = ['name', 'platform', 'difficulty', 'operating_system', 'target_ip', 'author', 'status', 'report_language', 'report_type', 'client_name', 'scope', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'scope': forms.Textarea(attrs={'rows': 3}),
        }

class EvidenceForm(BaseStyledForm):
    screenshots = MultipleFileField(required=False)
    
    class Meta:
        model = Evidence
        fields = ['phase', 'title', 'command', 'output', 'explanation', 'order']
        widgets = {
            'command': forms.Textarea(attrs={'rows': 3, 'class': 'font-monospace'}),
            'output': forms.Textarea(attrs={'rows': 5, 'class': 'font-monospace'}),
            'explanation': forms.Textarea(attrs={'rows': 4}),
        }

class VulnerabilityForm(BaseStyledForm):
    screenshots = MultipleFileField(required=False)

    class Meta:
        model = Vulnerability
        fields = [
            'title', 'vulnerability_type', 'severity', 'affected_service', 
            'affected_port', 'cve', 'how_identified', 'evidence', 
            'impact', 'recommendation', 'order'
        ]
        widgets = {
            'how_identified': forms.Textarea(attrs={'rows': 3}),
            'evidence': forms.Textarea(attrs={'rows': 4, 'class': 'font-monospace'}),
            'impact': forms.Textarea(attrs={'rows': 3}),
            'recommendation': forms.Textarea(attrs={'rows': 3}),
        }

class ExploitForm(BaseStyledForm):
    screenshots = MultipleFileField(required=False)

    class Meta:
        model = Exploit
        fields = [
            'name', 'vulnerability', 'exploit_type', 'objective', 
            'cve', 'url', 'local_path', 'affected_service', 'affected_port',
            'command_used', 'output', 'result', 'explanation', 'order'
        ]
        widgets = {
            'command_used': forms.Textarea(attrs={'rows': 3, 'class': 'font-monospace'}),
            'output': forms.Textarea(attrs={'rows': 5, 'class': 'font-monospace'}),
            'result': forms.Textarea(attrs={'rows': 3}),
            'explanation': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        machine = kwargs.pop('machine', None)
        super().__init__(*args, **kwargs)
        if machine:
            self.fields['vulnerability'].queryset = Vulnerability.objects.filter(machine=machine)

class ScreenshotForm(BaseStyledForm):
    class Meta:
        model = Screenshot
        fields = [
            'image', 'phase', 'title', 'caption', 'description', 
            'evidence', 'vulnerability', 'exploit', 'order'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        machine = kwargs.pop('machine', None)
        super().__init__(*args, **kwargs)
        if machine:
            self.fields['evidence'].queryset = Evidence.objects.filter(machine=machine)
            self.fields['vulnerability'].queryset = Vulnerability.objects.filter(machine=machine)
            self.fields['exploit'].queryset = Exploit.objects.filter(machine=machine)
            
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Check extension or content type
            valid_extensions = ['.png', '.jpg', '.jpeg', '.webp']
            import os
            ext = os.path.splitext(image.name)[1].lower()
            if ext not in valid_extensions:
                raise forms.ValidationError(f"Unsupported file extension. Allowed are: {', '.join(valid_extensions)}")
        return image

class FlagForm(BaseStyledForm):
    class Meta:
        model = Flag
        fields = ['flag_type', 'phase', 'value', 'location', 'obtained_as_user', 'found_commands', 'notes', 'censored']
        widgets = {
            'found_commands': forms.Textarea(attrs={'rows': 3, 'class': 'font-monospace'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
