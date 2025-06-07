from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Body
from fastapi.staticfiles import StaticFiles
from dataclasses import dataclass
from typing import Dict, Deque
from collections import deque

app = FastAPI()

# Serve static files such as game.html
app.mount("/", StaticFiles(directory=".", html=True), name="static")

@dataclass
class Session:
    player1: str
    player2: str

waiting_players: Deque[str] = deque()
sessions: Dict[str, Session] = {}
websockets: Dict[str, WebSocket] = {}

@app.post("/matchmake")
async def matchmake(player_id: str = Body(..., embed=True)):
    """Put player in queue and pair with opponent if available."""
    if waiting_players:
        opponent = waiting_players.popleft()
        session = Session(player1=opponent, player2=player_id)
        sessions[player_id] = session
        sessions[opponent] = session
        opponent_ws = websockets.get(opponent)
        if opponent_ws:
            await opponent_ws.send_json({"event": "matched", "opponent": player_id})
        return {"status": "matched", "opponent": opponent}
    else:
        waiting_players.append(player_id)
        return {"status": "waiting"}

@app.websocket("/ws/{player_id}")
async def websocket_endpoint(websocket: WebSocket, player_id: str):
    await websocket.accept()
    websockets[player_id] = websocket
    try:
        while True:
            data = await websocket.receive_json()
            session = sessions.get(player_id)
            if session:
                opponent_id = session.player1 if session.player2 == player_id else session.player2
                opp_ws = websockets.get(opponent_id)
                if opp_ws:
                    await opp_ws.send_json({"event": "message", "from": player_id, "data": data})
    except WebSocketDisconnect:
        websockets.pop(player_id, None)
