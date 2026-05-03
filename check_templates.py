import os
import django
from django.conf import settings
from django.template import Engine
from django.template.exceptions import TemplateSyntaxError

# configure minimum settings
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
    }]
)
django.setup()

engine = Engine.get_default()

template_dir = os.path.join('reports', 'templates', 'reports')

for file in os.listdir(template_dir):
    if not file.endswith('.html'): continue
    path = os.path.join(template_dir, file)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    try:
        engine.from_string(content)
    except TemplateSyntaxError as e:
        print(f"Error in {file}: {e}")
    except Exception as e:
        print(f"Other error in {file}: {e}")
