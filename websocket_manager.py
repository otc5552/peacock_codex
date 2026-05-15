from fastapi import WebSocket


class WebsocketManager:

    def __init__(self):

        self.clients = []

    async def connect(

        self,

        websocket: WebSocket
    ):

        await websocket.accept()

        self.clients.append(
            websocket
        )

    async def send(

        self,

        message
    ):

        for client in self.clients:

            await client.send_text(
                message
            )