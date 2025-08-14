import re

from fastapi import Request

from backend.api.entities.user import User
from backend.exceptions import NotPermittedException


def create_path_table():
    """権限管理テーブルを作成する

    Returns:
        dict : 権限コードがキーで、その権限を持つ人がアクセス可能なパス(正規表現)のリストを値にする辞書
    """
    # 一般利用者がアクセスできるページ
    for_all_user = [
        r"^/$",
        r"^/user/\d{1,10}/disp$",
        r"^/user/\d{1,10}/edit$",
        r"^/user_entry$",
    ]

    return {
        0: for_all_user,
        99: [r".{1,255}"],  # 全ての文字列にマッチ（管理者向け）
    }


# 権限テーブル作成実施
path_table = create_path_table()


def check_permission(request: Request, user: User):
    """指定されたユーザーがリクエストされたページにアクセスできるかどうかをチェックする

    Args:
        request (Request): リクエスト
        user (User): ユーザー

    Raises:
        NotPermittedException: アクセスできない場合にスローされる例外
    """
    paths = path_table.get(user.authority_code)
    for path in paths:
        if re.match(path, request.url.path):
            return
    raise NotPermittedException()
