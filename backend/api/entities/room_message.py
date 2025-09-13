from sqlalchemy import ForeignKey, Integer, Unicode
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.api.entities.base import Base

"""
    RoomMessage
"""


class RoomMessage(Base):

    __tablename__ = "t_room_message"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    """id（Key）"""

    room_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("t_room.id"), nullable=False
    )
    """room_member_id """

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("m_user.id"), nullable=False
    )
    """送信者（ユーザ）"""

    message: Mapped[str] = mapped_column(Unicode(1000), nullable=False)
    """メッセージ"""

    # リレーション
    room = relationship("Room", back_populates="messages")
    user = relationship("User", lazy="joined")
