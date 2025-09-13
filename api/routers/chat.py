import math
from datetime import datetime
from os import getenv
from typing import Dict, List, Optional
from urllib.parse import unquote

from fastapi import APIRouter, Cookie, Depends, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from api.entities.room_message import RoomMessage
from api.entities.user import User
from api.services import auth
from api.services import room as s_room
from api.std import define

# 初期設定
router = APIRouter()
router.mount("/static", StaticFiles(directory="ui/static"), name="static")
templates = Jinja2Templates(directory="ui/templates")


# 接続管理
class ConnectionManager:
    def __init__(self):
        # {room_id: List[{"websocket": WebSocket, "user_id": str, "user_name": str}]}
        self.active_connections: Dict[str, List[Dict]] = {}

    async def connect(
        self, websocket: WebSocket, room_id: str, user_id: str, user_name: str
    ):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []

        self.active_connections[room_id].append(
            {"websocket": websocket, "user_id": user_id, "user_name": user_name}
        )

    def disconnect(self, websocket: WebSocket):
        for room_id, connections in self.active_connections.items():
            for conn in connections:
                if conn["websocket"] == websocket:
                    connections.remove(conn)
                    break

    async def broadcast(self, room_id: str, sender_name: str, message: str):
        if room_id not in self.active_connections:
            return
        for conn in self.active_connections[room_id]:
            await conn["websocket"].send_json(
                {"sender": sender_name, "message": message}
            )


manager = ConnectionManager()


@router.get("/chat/{p_room_id}/form")
def room_form(
    request: Request,
    p_room_id: int,
    login_user: User = Depends(auth.check_auth),
):
    """
    ルーム情報入力画面：ロード
    """

    # ルームクラスのインスタンス生成
    e_room = s_room.get_room(p_room_id)

    return templates.TemplateResponse(
        "chat.html",
        {
            "request": request,
            "room": e_room,
            "result": "",
            "sys_msg": "",
            "login_user": login_user,
        },
    )


@router.websocket("/ws/{room_id}/{user_id}/{user_name}")
async def websocket_endpoint(
    websocket: WebSocket, room_id: str, user_id: str, user_name: str
):
    await manager.connect(websocket, room_id, user_id, user_name)
    try:
        while True:
            message = await websocket.receive_text()

            # メッセージクラスへセット
            e_message = RoomMessage()
            e_message.room_id = room_id
            e_message.user_id = user_id
            e_message.message = message

            # メッセージ登録
            s_room.entry_message(e_message)

            # room_id に接続している全員に user_name で送信
            await manager.broadcast(
                room_id,
                user_name,
                message,
            )

    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.get("/chat/{p_room_id}/api")
def chat_set_message(p_room_id: int):
    """
    チャット画面：ロード（APIコール）
    """
    # ルームクラスのインスタンス生成
    e_room = s_room.get_room(p_room_id)

    return {
        "messages": e_room.messages,
    }
