import math
from datetime import datetime
from os import getenv
from urllib.parse import quote

from fastapi import APIRouter, Cookie, Depends, Form, Request
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from backend.api.entities.user import User
from backend.api.services import user as s_user
from backend.api.std import define, func
from backend.api.services import auth


# 初期設定
router = APIRouter()
router.mount("/static", StaticFiles(directory="backend/ui/static"), name="static")
templates = Jinja2Templates(directory="backend/ui/templates")


@router.get("/user/list")
def user_list(
    request: Request,
    txt_mail_address: str = Cookie(""),
    txt_user_name: str = Cookie(""),
    hdn_page_no: int = Cookie(0),
    sel_row_max: int = Cookie(define.SEARCH_LIST_DISP_CNT[0]),
    login_user: User = Depends(auth.check_auth),
):
    """
    ユーザ 一覧画面
    """
    # URLパラメータのデコード実施
    txt_user_name = s_user.set_search_decode(txt_user_name)

    # 検索処理実施
    if hdn_page_no != 0:
        user_list, rec_count = s_user.find_users(
            txt_mail_address,
            txt_user_name,
            (hdn_page_no - 1) * sel_row_max,
            sel_row_max,
        )
    else:
        # 初回ロード時
        rec_count = 0
        hdn_page_no = 1
        user_list = []

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
        "user_list.html",
        {
            "request": request,
            "txt_mail_address": txt_mail_address,
            "txt_user_name": txt_user_name,
            "user_list": user_list,
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


@router.get("/user/list/download")
def user_list_download(
    txt_mail_address: str = Cookie(""),
    txt_user_name: str = Cookie(""),
    login_user: User = Depends(auth.check_auth),
):
    """
    ユーザ 一覧画面 ダウンロード処理
    """

    # URLパラメータのデコード実施
    txt_user_name = s_user.set_search_decode(txt_user_name)

    # 検索処理実施
    user_list, rec_count = s_user.find_users(txt_mail_address, txt_user_name, -1, -1)

    # エクセル生成
    xl = s_user.create_download_file(user_list)

    # ファイル名に使用するタイムスタンプ文字列生成
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d%H%M%S")

    return StreamingResponse(
        content=xl,
        headers={
            "Content-Disposition": f'attachment; filename="{quote(define.USER_DOWNLOAD_FILE_NAME)}_{timestamp}.xlsx"'
        },
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@router.get("/user/new")
def user_form_new(
    request: Request,
    login_user: User = Depends(auth.check_auth),
):
    return user_form_edit(request, 0, "new", login_user=login_user)


@router.get("/user/{p_user_id}/{mode}")
def user_form_edit(
    request: Request,
    p_user_id: int,
    mode: str,
    login_user: User = Depends(auth.check_auth),
):
    """
    ユーザ情報入力画面：ロード
    """

    # ユーザクラスのインスタンス生成
    e_user = s_user.get_user(p_user_id)

    # 権限リスト取得
    select_input_dict = s_user.get_selected_lists()

    return templates.TemplateResponse(
        "user_form.html",
        {
            "request": request,
            "user": e_user,
            "auth_list": select_input_dict["authority"],
            "page_max_disp_modal": define.PAGE_MAX_DISP_MODAL,
            "mode": mode,
            "result": "",
            "sys_msg": "",
            "login_user": login_user,
        },
    )


@router.post("/user_entry")
def user_entry(
    request: Request,
    hdn_user_id: str = Form(""),
    txt_mail_address: str = Form(""),
    txt_user_name: str = Form(""),
    txt_password: str = Form(""),
    sel_auth_code: str = Form(""),
    chk_del_flag: bool = Form(False),
    login_user: User = Depends(auth.check_auth),
):
    """
    ユーザ入力画面：登録・更新処理
    """

    # ユーザクラスのインスタンス生成
    e_user = s_user.get_user(int(hdn_user_id) if hdn_user_id != "" else 0)

    # 入力値取得
    e_user.mail_address = txt_mail_address
    e_user.user_name = txt_user_name
    e_user.hashed_password = (
        func.convert_password(txt_password) if txt_password != "" else ""
    )
    e_user.authority_code = int(sel_auth_code) if sel_auth_code != "" else 0
    e_user.del_flag = chk_del_flag

    # ▼登録処理
    if e_user.id is None:
        # ▼新規

        # 入力チェック
        is_valid, sys_msg = s_user.check_user(e_user, "new")
        if is_valid:
            e_user = s_user.create_user(e_user)
            # リターンコード設定
            sys_msg = "登録処理が正常に完了しました。"
            result = "complete"
            mode = "disp"

        else:
            result = "error"
            mode = "new"

    else:
        # ▼更新
        # 入力チェック
        is_valid, sys_msg = s_user.check_user(e_user, "update")
        if is_valid:
            e_user = s_user.update_user(e_user)
            # リターンコード設定
            sys_msg = "更新処理が正常に完了しました。"
            result = "complete"
            mode = "disp"

        else:
            result = "error"
            mode = "edit"

    # 権限リスト取得
    select_input_dict = s_user.get_selected_lists()

    return templates.TemplateResponse(
        "user_form.html",
        {
            "request": request,
            "user": e_user,
            "auth_list": select_input_dict["authority"],
            "page_max_disp_modal": define.PAGE_MAX_DISP_MODAL,
            "mode": mode,
            "result": result,
            "sys_msg": sys_msg,
            "login_user": login_user,
        },
    )
