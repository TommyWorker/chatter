class AuthenticationException(Exception):
    """認証エラー"""

    pass


class AuthorizationException(Exception):
    """認可エラー"""

    def __init__(self, error_type: str):
        self.error_type = error_type


class NotPermittedException(Exception):
    """アクセス不可エラー"""

    pass
