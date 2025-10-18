"""
ASGI config for kwl project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
from dotenv import load_dotenv
load_dotenv()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kwl.settings')

import django
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from authentication.middleware import JWTParamAuthMiddleware
import course.routing
import quiz.routing

application = ProtocolTypeRouter({
  "http": get_asgi_application(),
  "websocket": JWTParamAuthMiddleware(
      URLRouter(
          course.routing.websocket_urlpatterns + quiz.routing.websocket_urlpatterns
      )
  ),
})
