from fastapi import WebSocket
from typing import List
import redis

REDIS_HOST = "redis"
REDIS_PORT = 6379
REDIS_DB = 0

class ConnectionManager:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True
        )
        self.redis_chat_key = "chat:messages"
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        self.redis_client.lpush(self.redis_chat_key, message)
        self.redis_client.ltrim(self.redis_chat_key, 0, 99)
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                self.disconnect(connection)

    def get_message_history(self) -> List[str]:
        messages = self.redis_client.lrange(self.redis_chat_key, 0, -1)
        return messages[::-1]