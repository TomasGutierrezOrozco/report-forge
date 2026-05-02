import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'report_forge.settings')
django.setup()

from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.datastructures import MultiValueDict
from reports.forms import EvidenceForm

files = MultiValueDict({
    'screenshots': [
        SimpleUploadedFile("file1.png", b"file_content_1", content_type="image/png"),
        SimpleUploadedFile("file2.png", b"file_content_2", content_type="image/png")
    ]
})
data = {
    'title': 'Test',
    'phase': 'reconnaissance',
    'command': 'ls',
    'order': 1
}
form = EvidenceForm(data, files)
print("Is valid?", form.is_valid())
print("Errors:", form.errors)
print("Cleaned screenshots:", form.cleaned_data.get('screenshots'))
