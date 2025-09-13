from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

"""
    entitiesの基底クラス
"""


class Base(DeclarativeBase):

    create_user: Mapped[str] = mapped_column(
        String(20), default="SYSTEM", nullable=False
    )
    """作成者"""

    create_date: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    """作成日時"""

    update_user: Mapped[str] = mapped_column(
        String(20), default="SYSTEM", nullable=False
    )
    """更新者"""

    update_date: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )
    """更新日時"""

    del_flag: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    """削除フラグ"""
