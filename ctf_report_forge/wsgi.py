import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ctf_report_forge.settings')

application = get_wsgi_application()
