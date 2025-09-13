from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from api.entities.user import User
from api.repositories.user import UserRepo
from api.services.permission import check_permission
from api.std import func

security = HTTPBasic()


def check_auth(
    request: Request, credentials: HTTPBasicCredentials = Depends(security)
) -> User:
    """
    ベーシック認証による認証処理
        Args:
            credentials認証情報
        Returns:
            User: ログイン者のユーザ情報
    """

    mail_address = credentials.username
    in_password = func.convert_password(credentials.password)

    login_user = UserRepo().find_by_address(mail_address)

    if login_user is None or login_user.hashed_password != in_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ユーザ名かパスワードが間違っています",
            headers={"WWW-Authenticate": "Basic"},
        )
    else:
        check_permission(request, login_user)
        return login_user


async def get_user_info(request: Request) -> str:
    """
    ユーザ情報の文字列生成
    Args:
        request > リクエストオブジェクト
    Returns:
        生成した文字列（ユーザID - ユーザ名）

    """
    credentials: HTTPBasicCredentials | None = await security(request)
    if credentials is None or credentials.username == "":
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Basic"},
        )
    mail_address = credentials.username
    try:
        login_user = UserRepo().find_by_account(mail_address)
        user_name = login_user.user_name if login_user is not None else ""

    except Exception:
        user_name = "ユーザ名不明"

    return f"{mail_address} - {user_name}"
