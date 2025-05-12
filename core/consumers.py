import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db.models import Count
from .models import Election, Vote

class LiveElectionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.election_id = self.scope['url_route']['kwargs']['election_id']
        self.room_group_name = f'election_{self.election_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get("action") == "update":
            await self.send_live_results()

    async def send_live_results(self):
        election = Election.objects.get(id=self.election_id)
        votes = (
            Vote.objects.filter(election=election)
            .values('candidate__name')
            .annotate(total_votes=Count('candidate'))
            .order_by('-total_votes')
        )

        total_voters = Vote.objects.filter(election=election).count()
        total_votes = election.voter_set.count()

        turnout = round((total_voters / total_votes) * 100, 2) if total_votes > 0 else 0

        # Mask actual vote numbers (Display percentage or relative standing)
        candidates_data = [
            {"name": v["candidate__name"], "votes": index + 1} for index, v in enumerate(votes)
        ]

        response_data = {
            "election": election.name,
            "candidates": candidates_data,
            "turnout": turnout
        }

        # Send the message to WebSocket group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "send_update",
                "data": response_data
            }
        )

    async def send_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))
