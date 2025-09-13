from sqlalchemy import Integer, Unicode
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.api.entities.base import Base

"""
    Room
"""


class Room(Base):

    __tablename__ = "t_room"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    """id（Key）"""

    room_name: Mapped[str] = mapped_column(Unicode(100), nullable=True)
    """ルーム名"""

    remarks: Mapped[str] = mapped_column(Unicode(500), nullable=True)
    """備考"""

    # リレーション
    members = relationship(
        "RoomMember", back_populates="room", lazy="joined", cascade="all, delete-orphan"
    )
    messages = relationship(
        "RoomMessage",
        back_populates="room",
        lazy="joined",
        cascade="all, delete-orphan",
    )
