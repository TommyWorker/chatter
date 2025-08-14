from sqlalchemy import Boolean, ForeignKey, Integer, String, Unicode
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.api.entities.base import Base

"""
    汎用マスタ
"""


class General(Base):

    __tablename__ = "m_general"

    category: Mapped[str] = mapped_column(
        String(40), ForeignKey("m_category.category"), primary_key=True
    )
    """カテゴリ（Key）"""

    code: Mapped[int] = mapped_column(Integer, primary_key=True)
    """コード（Key）"""

    code_value: Mapped[str] = mapped_column(Unicode(200), nullable=False)
    """値"""

    code_reserve01_text: Mapped[str] = mapped_column(Unicode(1000), nullable=True)
    """予備テキスト01"""

    code_reserve02_text: Mapped[str] = mapped_column(Unicode(1000), nullable=True)
    """予備テキスト02"""

    code_reserve01_flag: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=True
    )
    """予備フラグ01"""

    code_reserve02_flag: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=True
    )
    """予備フラグ02"""

    code_reserve01_code: Mapped[str] = mapped_column(String(20), nullable=True)
    """予備コード01"""

    code_reserve02_code: Mapped[str] = mapped_column(String(20), nullable=True)
    """予備コード02"""

    sort_key: Mapped[int] = mapped_column(Integer, default=1000, nullable=False)
    """ソートキー"""

    remarks: Mapped[str] = mapped_column(Unicode(500), nullable=True)
    """備考"""

    # カテゴリマスタへリレーション
    r_category = relationship(
        "Category", foreign_keys=[category], lazy="joined", viewonly=True
    )
