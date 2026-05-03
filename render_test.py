import os
import django
from django.conf import settings
from django.test import RequestFactory

settings.configure(
    INSTALLED_APPS=[
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'reports',
    ],
    TEMPLATES=[{
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reports', 'templates')],
        'APP_DIRS': True,
    }],
    DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': 'db.sqlite3'}},
    ROOT_URLCONF='ctf_report_forge.urls'
)
django.setup()

from reports.models import Machine
from django.template.loader import render_to_string
from reports.forms import FlagForm, EvidenceForm, VulnerabilityForm, ExploitForm, ScreenshotForm

m = Machine.objects.first()
if not m:
    print("No machines")
else:
    for form_class, tpl in [
        (FlagForm, 'reports/flag_form.html'),
        (EvidenceForm, 'reports/evidence_form.html'),
        (VulnerabilityForm, 'reports/vulnerability_form.html'),
        (ExploitForm, 'reports/exploit_form.html'),
        (ScreenshotForm, 'reports/screenshot_form.html')
    ]:
        try:
            form = form_class()
            html = render_to_string(tpl, {'form': form, 'machine': m})
            print(f"OK: {tpl}")
        except Exception as e:
            print(f"Error rendering {tpl}: {e}")
