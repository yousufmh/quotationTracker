"""
WSGI config for qoutationSystem project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""
import os
import sys
import site
# Add the site-packages of the chosen virtualenv to work with
site.addsitedir('')
# Add the app's directory to the PYTHONPATH
sys.path.append('')
sys.path.append('')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qoutationSystem.settings')
# Activate your virtual env
activate_env=os.path.expanduser("/home/admin1/qoutationSystem/quotationENV/bin/activate_this.py")
execfile(activate_env, dict(__file__=activate_env))
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()