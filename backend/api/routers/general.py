import math
from datetime import datetime
from os import getenv
from urllib.parse import quote

from fastapi import APIRouter, Cookie, Depends, Form, Request
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from backend.api.entities.general import General
from backend.api.entities.user import User
from backend.api.services import general as s_general
from backend.api.std import define
from backend.api.services import auth


# 初期設定
router = APIRouter()
router.mount("/static", StaticFiles(directory="backend/ui/static"), name="static")
templates = Jinja2Templates(directory="backend/ui/templates")


@router.get("/general/list")
def general_list(
    request: Request,
    sel_category: str = Cookie(""),
    txt_code_value: str = Cookie(""),
    hdn_page_no: int = Cookie(0),
    sel_row_max: int = Cookie(define.SEARCH_LIST_DISP_CNT[0]),
    login_user: User = Depends(auth.check_auth),
):
    """
    マスタメンテナンス（汎用マスタ） 一覧画面
    """

    category_list = s_general.get_select_list()

    # URLパラメータのデコード実施
    sel_category, txt_code_value = s_general.set_search_decode(
        sel_category, txt_code_value
    )

    # 検索処理実施
    if hdn_page_no != 0:
        general_list, rec_count = s_general.search_general_list(
            sel_category, txt_code_value, (hdn_page_no - 1) * sel_row_max, sel_row_max
        )
    else:
        # 初回ロード時
        rec_count = 0
        hdn_page_no = 1
        general_list = []

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
        "general_list.html",
        {
            "request": request,
            "sel_category": sel_category,
            "txt_code_value": txt_code_value,
            "category_list": category_list,
            "general_list": general_list,
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


@router.get("/general/list/download")
def general_list_download(
    sel_category: str = Cookie(""),
    txt_code_value: str = Cookie(""),
    login_user: User = Depends(auth.check_auth),
):
    """
    機種情報 一覧画面 ダウンロード処理
    """

    # URLパラメータのデコード実施
    sel_category, txt_code_value = s_general.set_search_decode(
        sel_category, txt_code_value
    )

    # 検索処理実施
    general_list, rec_count = s_general.search_general_list(
        sel_category, txt_code_value, -1, -1
    )

    # エクセル生成
    xl = s_general.create_download_file(general_list)

    # ファイル名に使用するタイムスタンプ文字列生成
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d%H%M%S")

    return StreamingResponse(
        content=xl,
        headers={
            "Content-Disposition": f'attachment; filename="{quote(define.GENERAL_DOWNLOAD_FILE_NAME)}_{timestamp}.xlsx"'
        },
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@router.get("/general/new")
def general_form_new(
    request: Request,
    sel_category: str = Cookie(""),
    login_user: User = Depends(auth.check_auth),
):
    return general_form_edit(request, p_category=sel_category, login_user=login_user)


@router.get("/general/{p_category}/{p_code}/{mode}")
def general_form_edit(
    request: Request,
    p_code: int = -1,
    p_category: str = "",
    mode: str = "edit",
    login_user: User = Depends(auth.check_auth),
):
    """
    汎用マスタ情報入力画面：ロード
    """

    # カテゴリのリストを取得する
    category_list = s_general.get_select_list()

    if p_code != -1:
        # 汎用マスタ情報管理クラスのインスタンス生成
        e_general = s_general.get_general(p_code, p_category)
    else:
        e_general = General()
        e_general.category = p_category

    return templates.TemplateResponse(
        "general_form.html",
        {
            "request": request,
            "category_list": category_list,
            "general": e_general,
            "mode": mode,
            "result": "",
            "sys_msg": "",
            "login_user": login_user,
        },
    )


@router.post("/general_entry")
def general_entry(
    request: Request,
    sel_category: str = Form(""),
    txt_code: str = Form(""),
    txt_code_value: str = Form(""),
    txt_sort_key: int = Form(1000),
    txt_remarks: str = Form(""),
    chk_del_flag: bool = Form(False),
    login_user: User = Depends(auth.check_auth),
):
    """
    汎用マスタ情報入力画面：登録・更新処理
    """

    # カテゴリのリストを取得する
    category_list = s_general.get_select_list()

    # 汎用マスタ管理クラスのインスタンス生成
    if txt_code:
        e_general = s_general.get_general(int(txt_code), sel_category)
    else:
        e_general = General()
        e_general.code = -1

    # 入力値取得
    e_general.category = sel_category
    e_general.code_value = txt_code_value
    e_general.sort_key = txt_sort_key
    e_general.remarks = txt_remarks
    e_general.del_flag = chk_del_flag

    is_unique = s_general.duplicate_check(e_general)

    if is_unique:
        # ▼登録処理
        if e_general.code == -1:
            # ▼新規
            e_general.code = s_general.create_general(e_general)
            sys_msg = "登録処理が正常に完了しました。"

        else:
            # ▼更新
            e_general = s_general.update_general(e_general)
            sys_msg = "更新処理が正常に完了しました。"

        # リターンコード設定
        result = "complete"
        mode = "disp"

    else:
        # リターンコード設定
        sys_msg = "入力されたカテゴリ、名称と完全に一致する情報が存在します。"
        result = "error"
        mode = "edit"

    return templates.TemplateResponse(
        "general_form.html",
        {
            "request": request,
            "category_list": category_list,
            "general": e_general,
            "mode": mode,
            "result": result,
            "sys_msg": sys_msg,
            "login_user": login_user,
        },
    )
