# Websocket connection routing, and background proceseses.

from django.conf.urls import url
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from server.websockets import WorkflowWebsocketConsumer

application = ProtocolTypeRouter({

    # WebSocket chat handler
    "websocket": AuthMiddlewareStack(
        URLRouter([
            url("^\d_$", WorkflowWebsocketConsumer)
        ])
    ),
})