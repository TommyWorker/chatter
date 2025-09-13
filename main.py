import importlib
import os
from pathlib import Path
from typing import Awaitable, Callable

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import Response

from api.entities.base import Base
from api.entities.user import User
from api.services import auth
from api.std import func, sql
from api.std.logging import log
from exceptions import (
    AuthenticationException,
    AuthorizationException,
    NotPermittedException,
)

# 環境変数を.evnより設定
load_dotenv(override=True)


# 初期設定
app = FastAPI()
base_dir = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=base_dir / "ui/static"), name="static")
templates = Jinja2Templates(directory=base_dir / "ui/templates")
router_directory = base_dir / "api/routers"
module_prefix = "api.routers."


# 各ルーターモジュールをInclude
for filepath in router_directory.glob("*.py"):
    if not filepath.name.startswith("__"):
        module_name = module_prefix + filepath.stem
        module = importlib.import_module(module_name)
        if hasattr(module, "router"):
            app.include_router(module.router)


# セキュリティ強化のためのミドルウェア
class SecurityHeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:

        try:

            # アクセスログ記録
            log.info(
                f"{await auth.get_user_info(request)} - {request.method} {request.url}"
            )

            # クロスサイトリクエストフォージェリ（CSRF）攻撃に対する対策
            #   リクエストのクッキーから"strict"という名前のクッキーを取得し、その値をrequest.state.strictに保存。
            request.state.strict = request.cookies.get("strict", None)
            #   POSTおよびDELETEメソッドでかつstrictクッキーが存在しない場合は例外発生
            if (
                request.method == "POST" or request.method == "DELETE"
            ) and not request.state.strict:
                raise NotPermittedException()

            # エンドポイント呼び出し
            response = await call_next(request)

            # Cookieを設定
            #   SameSite属性: samesite="strict"を設定することで、クッキーが同一サイトからのリクエストに対してのみ送信されるようにする。
            #                これにより、クロスサイトリクエストフォージェリ（CSRF）攻撃を防ぐ。
            #   HttpOnly属性: httponly=Trueを設定することで、クッキーがJavaScriptからアクセスできないようにする。
            #                これにより、クッキーのセキュリティが向上する。
            #   Secure属性:   secure=Trueを設定することで、クッキーがHTTPS接続でのみ送信されるようにする。
            #                これにより、クッキーの盗聴を防ぐ。
            response.set_cookie(
                "strict",
                "strict",
                (24 * 60 * 60),
                path="/",
                samesite="strict",
                httponly=True,
                secure=True,
            )

            # CSPヘッダをレスポンスに追加する
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; script-src-attr 'self' 'unsafe-inline'"
            )

            # frame のソースを同一サイト内に限定する
            response.headers["X-Frame-Options"] = "SAMEORIGIN"

            return response

        except HTTPException as h_exc:
            # 401が発生したら認証ダイアログを表示
            if h_exc.status_code == 401:
                return Response(
                    content=h_exc.detail,
                    status_code=h_exc.status_code,
                    headers={"WWW-Authenticate": "Basic"},
                )
            else:
                log.error(f"HTTPException: {h_exc.detail}")
                raise


# SecurityHeaderMiddleware を追加
app.add_middleware(SecurityHeaderMiddleware)


# SessionMiddleware を追加
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_KEY"),
    https_only=True,
)


@app.get("/")
async def root(request: Request, login_user: User = Depends(auth.check_auth)):
    """
    ルートURL（Topページへリダイレクト）
    """
    log.info(f"{await auth.get_user_info(request)} - ログインしました")
    return RedirectResponse("/room/list")


@app.get("/logout")
async def logout(request: Request):
    """
    ログアウト処理
    """
    log.info(f"{await auth.get_user_info(request)} - ログアウトしました")

    # セッション情報をクリアする
    request.session.clear()

    return templates.TemplateResponse(
        "system_info.html",
        {"request": request, "title": "ログアウト", "message": "ログアウトしました。"},
    )


@app.get("/healthcheck")
def healthcheck():
    """
    ECSのヘルスチェック用エンドポイント
    """
    return {"message": "healthcheck"}


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
        {"request": request, "title": "認可エラー", "message": "権限がありません。"},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    例外エラー処理
    """
    # 本番では汎用メッセージ、開発環境のみ詳細表示
    is_dev = os.getenv("APP_ENV") == "dev"
    message = func.get_exc_info() if is_dev else "想定外のエラーが発生しました。"
    log.error(f"Exception: {exc}")

    return templates.TemplateResponse(
        "system_info.html",
        {"request": request, "title": "エラー", "message": message},
    )
