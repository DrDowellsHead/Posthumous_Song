"""
ASGI config for PosthumousSong project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

""" In this line below, changing the value after 'settings',
    determines which data exchange standard will be used when starting the server. """
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PosthumousSong.settings.prod')

application = get_asgi_application()
