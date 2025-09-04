from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from manager import ConnectionManager

app = FastAPI()
templates = Jinja2Templates(directory="templates")
manager = ConnectionManager()

@app.get("/", response_class=HTMLResponse)
async def chat_interface(request: Request):
    message_history = manager.get_message_history()
    return templates.TemplateResponse(
        "chat.html", 
        {"request": request, "message_history": message_history}
    )

@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    await manager.connect(websocket)
    
    welcome_message = f"Сервер: {username} присоединился к чату!"
    await manager.broadcast(welcome_message)

    try:
        while True:
            data = await websocket.receive_text()
            message_text = f"{username}: {data}"
            await manager.broadcast(message_text)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        leave_message = f"Сервер: {username} покинул чат."
        await manager.broadcast(leave_message)