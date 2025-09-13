import math
from datetime import datetime
from os import getenv
from typing import List, Optional
from urllib.parse import unquote

from fastapi import APIRouter, Cookie, Depends, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from backend.api.entities.room import Room
from backend.api.entities.room_member import RoomMember
from backend.api.entities.user import User
from backend.api.services import auth
from backend.api.services import room as s_room
from backend.api.std import define, func


# ルーム登録時の受信データのスキーマを定義
class RoomEntry(BaseModel):
    room_id: Optional[str] = None
    members: List[str]
    room_name: Optional[str] = None
    remarks: Optional[str] = None


# 初期設定
router = APIRouter()
router.mount("/static", StaticFiles(directory="backend/ui/static"), name="static")
templates = Jinja2Templates(directory="backend/ui/templates")


@router.get("/room/list")
def room_list(
    request: Request,
    txt_room_name: str = Cookie(""),
    hdn_page_no: int = Cookie(0),
    sel_row_max: int = Cookie(define.SEARCH_LIST_DISP_CNT[0]),
    login_user: User = Depends(auth.check_auth),
):
    """
    ルーム 一覧画面
    """
    # URLパラメータのデコード実施
    txt_room_name = unquote(txt_room_name)

    # 検索処理実施
    if hdn_page_no != 0:
        room_list, rec_count = s_room.find_rooms(
            txt_room_name,
            login_user.id,
            (hdn_page_no - 1) * sel_row_max,
            sel_row_max,
        )
    else:
        # 初回ロード時
        rec_count = 0
        hdn_page_no = 1
        room_list = []

    # ▼検索処理
    # 一覧のスタートページ
    start_page = (
        math.floor(hdn_page_no / (define.PAGE_MAX_DISP)) * define.PAGE_MAX_DISP + 1
    )
    if hdn_page_no % define.PAGE_MAX_DISP == 0:
        start_page -= define.PAGE_MAX_DISP

    # 全ページ数
    page_count = math.ceil(rec_count / sel_row_max)

    # 一度に表示するページ数（最終ページだけ少ない）
    if rec_count <= define.PAGE_MAX_DISP:
        page_max_disp = 1
    elif start_page + define.PAGE_MAX_DISP - 1 > page_count:
        page_max_disp = page_count - start_page + 1
    else:
        page_max_disp = define.PAGE_MAX_DISP

    return templates.TemplateResponse(
        "room_list.html",
        {
            "request": request,
            "room_name": txt_room_name,
            "room_list": room_list,
            "hdn_page_no": hdn_page_no,
            "row_max_list": define.SEARCH_LIST_DISP_CNT,
            "sel_row_max": sel_row_max,
            "start_page": start_page,
            "page_count": page_count,
            "page_max_disp": page_max_disp,
            "rec_count": rec_count,
            "result": "",
            "sys_msg": "",
            "login_user": login_user,
        },
    )


@router.get("/room/new")
def room_form_new(
    request: Request,
    login_user: User = Depends(auth.check_auth),
):
    return room_form_edit(request, 0, "new", login_user=login_user)


@router.get("/room/{p_room_id}/{mode}")
def room_form_edit(
    request: Request,
    p_room_id: int,
    mode: str,
    login_user: User = Depends(auth.check_auth),
):
    """
    ルーム情報入力画面：ロード
    """

    # ルームクラスのインスタンス生成
    e_room = s_room.get_room(p_room_id)

    # 選択メンバーリスト取得
    select_input_dict = s_room.get_selected_lists(login_user.id)

    return templates.TemplateResponse(
        "room_form.html",
        {
            "request": request,
            "room": e_room,
            "select_member_list": select_input_dict["members"],
            "mode": mode,
            "result": "",
            "sys_msg": "",
            "login_user": login_user,
        },
    )


@router.get("/room/{p_room_id}/{mode}/api")
def room_set_member(p_room_id: int):
    """
    ルーム情報入力画面：ロード（APIコール）
    """
    # ルームクラスのインスタンス生成
    e_room = s_room.get_room(p_room_id)

    return {
        "members": e_room.members,
    }


@router.post("/room_entry")
def room_entry(
    data: RoomEntry,
    login_user: User = Depends(auth.check_auth),
):
    """
    ルーム情報入力画面：登録・更新処理
    """

    # ユーザクラスのインスタンス生成
    e_room = s_room.get_room(int(data.room_id) if data.room_id != "" else 0)

    # 入力値取得
    e_room.room_name = data.room_name
    e_room.remarks = data.remarks
    data.members.append(login_user.mail_address)

    # ▼登録処理
    if e_room.id is None:
        # ▼新規
        e_room = s_room.create_room(e_room, data.members)
        # リターンコード設定
        sys_msg = "登録処理が正常に完了しました。"
        result = "complete"

    else:
        # ▼更新
        e_room = s_room.update_room(e_room, data.members)
        # リターンコード設定
        sys_msg = "更新処理が正常に完了しました。"
        result = "complete"

    return {
        "result": result,
        "sys_msg": sys_msg,
        "login_user": login_user,
    }
