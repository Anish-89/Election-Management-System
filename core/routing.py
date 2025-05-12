from django.urls import path
from .consumers import LiveElectionConsumer

websocket_urlpatterns = [
    path("ws/election/<int:election_id>/", LiveElectionConsumer.as_asgi()),
]

