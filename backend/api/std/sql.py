from os import getenv
from typing import List, Optional

from sqlalchemy import Connection, Engine, Row, text
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker

"""
    Sql
    汎用的なSQL処理を束ねたモジュール
    各repositoriesにImportすることを想定
"""


def create_sql_engine() -> Engine:
    """
    SQL実行エンジンを作成 (PostgreSQL用)
    """

    # 環境変数から接続情報を取得
    user = getenv("DB_USER")
    password = getenv("DB_PW")
    host = getenv("DB_SERVER")
    port = getenv("DB_PORT")
    database = getenv("DB_DATABASE")

    db_url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"

    return create_engine(
        db_url,
        pool_size=10,
        max_overflow=30,
        pool_pre_ping=True,
    )


engine = create_sql_engine()
Session = sessionmaker(bind=engine)


def execute(sql: str, connection: Connection, params: dict = {}):
    """
    指定したSQLを実行
    """
    return connection.execute(text(sql), params)


def select(
    sql: str, params: dict = {}, connection: Optional[Connection] = None
) -> List[Row]:
    """
    指定したSQLを用いて検索処理を実行
    検索結果行一覧をリストで返す
    """
    if connection is None:
        with engine.begin() as connection:
            return execute(sql, connection, params).fetchall()
    else:
        return execute(sql, connection, params).fetchall()


def insert(sql: str, params: dict = {}, connection: Optional[Connection] = None) -> int:
    """
    指定したSQLを用いて新規追加処理を実行
    新規追加した行のIDを返す
    PostgreSQLでは RETURNING id を使用
    """
    returning_sql = f"{sql} RETURNING id"

    if connection is None:
        with engine.begin() as connection:
            result = execute(returning_sql, connection, params)
            return result.fetchone()[0]
    else:
        result = execute(returning_sql, connection, params)
        return result.fetchone()[0]


def update(sql: str, params: dict = {}, connection: Optional[Connection] = None) -> int:
    """
    指定したSQLを用いて更新処理を実行
    更新行数を返す
    """
    if connection is None:
        with engine.begin() as connection:
            return execute(sql, connection, params).rowcount
    else:
        return execute(sql, connection, params).rowcount


def delete(sql: str, params: dict = {}, connection: Optional[Connection] = None) -> int:
    """
    指定したSQLを用いて削除処理を実行
    削除行数を返す
    """
    return update(sql, params, connection)
