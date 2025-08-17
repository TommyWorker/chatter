from sqlalchemy import Integer, Unicode, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.api.entities.base import Base

"""
    RoomMessage
"""

class RoomMessage(Base):

    __tablename__ = "t_room_message"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    """id（Key）"""

    room_member_id: Mapped[int] = mapped_column(Integer, ForeignKey("t_room_member.id"), nullable=False)
    """room_member_id """
    
    message: Mapped[str] = mapped_column(Unicode(1000), nullable=False)
    """メッセージ"""
    
    # メンバーへリレーション
    members = relationship("RoomMember", back_populates="messages")