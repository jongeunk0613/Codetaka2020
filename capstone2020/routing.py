from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import codetaka.routing

application = ProtocolTypeRouter({
   'websocket': AuthMiddlewareStack(
      URLRouter(
         codetaka.routing.websocket_urlpatterns
      )
   ),
})
