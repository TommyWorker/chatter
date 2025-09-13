from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.api.entities.base import Base

"""
    RoomMember
"""


class RoomMember(Base):

    __tablename__ = "t_room_member"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    """id（Key）"""

    room_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("t_room.id"), nullable=False
    )
    """room_id """

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("m_user.id"), nullable=False
    )
    """user_id """

    # ルームへリレーション
    room = relationship("Room", back_populates="members")

    # ユーザへリレーション
    user = relationship("User", lazy="joined")
