import math
from urllib.parse import unquote

from datetime import datetime
from os import getenv

from fastapi import APIRouter, Cookie, Depends, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from backend.api.entities.room import Room
from backend.api.entities.user import User
from backend.api.services import room as s_room
from backend.api.std import define, func
from backend.api.services import auth


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

    # ユーザクラスのインスタンス生成
    e_room = s_room.get_room(p_room_id)

    # ユーザリスト取得
    select_input_dict = s_room.get_selected_lists(login_user.id)

    return templates.TemplateResponse(
        "room_form.html",
        {
            "request": request,
            "room": e_room,
            "member_list": select_input_dict["member"],
            "mode": mode,
            "result": "",
            "sys_msg": "",
            "login_user": login_user,
        },
    )