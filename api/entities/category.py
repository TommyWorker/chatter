from sqlalchemy import Boolean, Integer, String, Unicode
from sqlalchemy.orm import Mapped, mapped_column

from api.entities.base import Base

"""
    カテゴリマスタ
"""


class Category(Base):

    __tablename__ = "m_category"

    category: Mapped[str] = mapped_column(String(40), primary_key=True)
    """カテゴリ"""

    display_name: Mapped[int] = mapped_column(Unicode(200), nullable=False)
    """表示名"""

    maintenance_flag: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    """メンテナンスフラグ（True：ユーザメンテ可）"""

    sort_key: Mapped[int] = mapped_column(Integer, default=1000, nullable=False)
    """ソートキー"""

    remarks: Mapped[str] = mapped_column(Unicode(500), nullable=True)
    """備考"""
