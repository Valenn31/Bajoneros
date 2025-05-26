import json
from channels.generic.websocket import AsyncWebsocketConsumer

class PedidosConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("pedidos", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("pedidos", self.channel_name)

    async def receive(self, text_data):
        pass  # No necesitas recibir mensajes del cliente

    async def nuevo_pedido(self, event):
        await self.send(text_data=json.dumps({
            'message': 'nuevo_pedido'
        }))