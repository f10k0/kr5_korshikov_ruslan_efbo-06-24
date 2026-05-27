from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, status
from fastapi.responses import JSONResponse
from app.routers import tasks, users, admin
from app.websocket_manager import room_manager
from app.dependencies import get_current_user
from app.schemas import User

app = FastAPI(title="Task Manager API")

app.include_router(tasks.router)
app.include_router(users.router)
app.include_router(admin.router)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.websocket("/ws/rooms/{room_id}")
async def websocket_room(websocket: WebSocket, room_id: str, username: str = None):
    if not username or not username.strip():
        await websocket.close(code=1008, reason="Username is required")
        return
    username = username.strip()
    await room_manager.connect(room_id, username, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")
            if msg_type == "message":
                text = data.get("text", "")
                if len(text) > 300:
                    await room_manager.send_to_user(room_id, username, {
                        "type": "error",
                        "detail": "Message is too long"
                    })
                else:
                    await room_manager.broadcast(room_id, {
                        "type": "message",
                        "room_id": room_id,
                        "username": username,
                        "text": text
                    })
    except WebSocketDisconnect:
        await room_manager.disconnect(room_id, username, websocket)

@app.get("/rooms/{room_id}/users")
async def get_room_users(room_id: str):
    users_list = room_manager.get_users(room_id)
    return {"room_id": room_id, "users": users_list}