import importlib
from pathlib import Path
import os
from dotenv import load_dotenv

from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from backend.api.entities.base import Base
from backend.api.entities.user import User
from backend.api.services import auth
from backend.api.std import sql, func

from backend.exceptions import (
    AuthenticationException,
    AuthorizationException,
)

# 環境変数を.evnより設定
load_dotenv(override=True)


# 初期設定
app = FastAPI()
base_dir = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=base_dir / "ui/static"), name="static")
templates = Jinja2Templates(directory=base_dir / "ui/templates")
router_directory = base_dir / "api/routers"
module_prefix = base_dir.name + ".api.routers."

# 各ルーターモジュールをInclude
for filepath in router_directory.glob("*.py"):
    if not filepath.name.startswith("__"):
        module_name = module_prefix + filepath.stem
        module = importlib.import_module(module_name)
        if hasattr(module, "router"):
            app.include_router(module.router)


@app.get("/")
def root(request: Request, login_user: User = Depends(auth.check_auth)):
    return templates.TemplateResponse(
        "top.html",
        {"request": request, "login_user": login_user},
    )


def drop_all_fk():
    """
    全ての外部制約をDROPする（PostgreSQL版）
    """
    rows = sql.select(
        """
        SELECT
            tc.constraint_name AS key,
            tc.table_name AS table
        FROM information_schema.table_constraints tc
        WHERE tc.constraint_type = 'FOREIGN KEY'
          AND tc.table_schema = 'public'
        """
    )

    for row in rows:
        drop_fk_sql = f'ALTER TABLE "{row.table}" DROP CONSTRAINT "{row.key}"'
        print("Execute:", drop_fk_sql)
        sql.update(drop_fk_sql)


def drop_all_tables():
    """
    全てのテーブルをDROPする（PostgreSQL版）
    """
    rows = sql.select(
        """
        SELECT table_name AS table
        FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_type = 'BASE TABLE'
        """
    )

    for row in rows:
        drop_table_sql = f'DROP TABLE "{row.table}" CASCADE'
        print("Execute:", drop_table_sql)
        sql.update(drop_table_sql)


def set_data_init():
    """
    マスタデータを初期設定
    """

    with open(base_dir / "data/data_init.sql", "r", encoding="utf-8") as file:
        sql_text = file.read()

    # セミコロンで分割
    statements = sql_text.split(";")

    for statement in statements:
        sql_query = statement.strip()
        if sql_query and not sql_query.startswith("--"):  # コメント行は除外
            sql.update(sql_query)
            

@app.post("/init/run")
def init_run(request: Request):
    """
    DB初期化
    """
    app_env = os.getenv("APP_ENV")

    # 開発環境かつDBの向け先が本番環境以外でのみ実施可能とする
    if app_env == "dev":

        # 外部制約を削除
        drop_all_fk()

        # テーブルを削除
        drop_all_tables()

        # entitiesクラス定義に基づきテーブル作成
        Base.metadata.create_all(sql.engine)

        # データ初期設定
        set_data_init()

        return templates.TemplateResponse(
            "system_info.html",
            {
                "request": request,
                "title": "DB初期化処理",
                "message": "DBを作成しました。",
            },
        )

    else:
        return templates.TemplateResponse(
            "system_info.html",
            {
                "request": request,
                "title": "不正な操作が実行されました",
                "message": "DBの初期化は、開発環境かつDBの向け先が本番環境以外でのみ実施可能です。",
            },
        )


@app.get("/init_database")
def init_database(request: Request):
    """
    DB初期化ページへ遷移
    """
    app_env = os.getenv("APP_ENV")

    # 開発環境かつDBの向け先が本番環境以外でのみ表示可能とする
    if app_env == "dev":
        return templates.TemplateResponse("init.html", {"request": request})

    else:
        return templates.TemplateResponse(
            "system_info.html",
            {
                "request": request,
                "title": "不正な操作が実行されました",
                "message": "DBの初期化ページは、開発環境かつDBの向け先が本番環境以外でのみ表示可能です。",
            },
        )


@app.exception_handler(AuthenticationException)
async def authentication_exception_handler(
    request: Request, exc: AuthenticationException
):
    """AuthenticationExceptionが発生した場合は / にリダイレクトする"""
    return RedirectResponse("/login")


@app.exception_handler(AuthorizationException)
async def authorization_exception_handler(
    request: Request, exc: AuthorizationException
):
    """AuthorizationExceptionが発生した場合はエラーページを表示する"""
    return templates.TemplateResponse(
        "system_info.html",
        {
            "request": request,
            "title": "認可エラー",
            "message": "ご利用のアカウントには本システムの利用権限がありません。\n"
            "お手数ですが、以下のエラータイプを添えてシステム管理者へお問い合わせをお願いいたします。\n\n"
            f"エラータイプ: {exc.error_type}",
        },
    )


@app.exception_handler(Exception)
async def http_exception_handler(request: Request, exc: Exception):
    """
    例外エラー処理
    """
    # 例外情報を取得
    message = func.get_exc_info(os.getenv("APP_ENV") or "")

    return templates.TemplateResponse(
        "system_info.html",
        {
            "request": request,
            "title": "想定外のエラーが発生しました",
            "message": message,
        },
    )