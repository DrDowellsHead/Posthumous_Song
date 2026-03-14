"""
WSGI config for PosthumousSong project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

""" In this line below, changing the value after 'settings',
    determines which data exchange standard will be used when starting the server. """
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PosthumousSong.settings.prod')

application = get_wsgi_application()
