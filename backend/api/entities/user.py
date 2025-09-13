from sqlalchemy import Integer, String, Unicode
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.api.entities.base import Base

"""
    ユーザマスタ
"""


class User(Base):

    __tablename__ = "m_user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    """id（Key）"""

    mail_address: Mapped[str] = mapped_column(String(514), unique=True, nullable=False)
    """メールアドレス"""

    user_name: Mapped[str] = mapped_column(Unicode(140), nullable=False)
    """名前"""

    hashed_password: Mapped[str] = mapped_column(String(514), nullable=False)
    """パスワード"""

    authority_code: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    """権限コード"""

    # 汎用マスタの権限コードへリレーション
    authority = relationship(
        "General",
        lazy="joined",
        viewonly=True,
        primaryjoin="and_(General.category == 'authority_code', foreign(General.code) == User.authority_code)",
    )
