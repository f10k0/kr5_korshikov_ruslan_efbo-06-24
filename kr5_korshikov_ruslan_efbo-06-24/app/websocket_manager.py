from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect

class RoomManager:
    def __init__(self):
        self.rooms: Dict[str, Dict[str, WebSocket]] = {}

    async def connect(self, room_id: str, username: str, websocket: WebSocket):
        await websocket.accept()
        if room_id not in self.rooms:
            self.rooms[room_id] = {}
        self.rooms[room_id][username] = websocket
        await self.broadcast(room_id, {
            "type": "system",
            "message": f"{username} joined the room"
        })

    async def disconnect(self, room_id: str, username: str, websocket: WebSocket):
        if room_id in self.rooms:
            self.rooms[room_id].pop(username, None)
            if not self.rooms[room_id]:
                del self.rooms[room_id]
        await self.broadcast(room_id, {
            "type": "system",
            "message": f"{username} left the room"
        })

    async def broadcast(self, room_id: str, payload: dict):
        if room_id in self.rooms:
            for ws in self.rooms[room_id].values():
                try:
                    await ws.send_json(payload)
                except:
                    pass

    async def send_to_user(self, room_id: str, username: str, payload: dict):
        if room_id in self.rooms and username in self.rooms[room_id]:
            try:
                await self.rooms[room_id][username].send_json(payload)
            except:
                pass

    def get_users(self, room_id: str) -> list:
        if room_id not in self.rooms:
            return []
        return list(self.rooms[room_id].keys())

room_manager = RoomManager()