from typing import Optional, Sequence, Tuple

from sqlalchemy import and_, func, select, asc, desc

from backend.api.entities.room import Room
from backend.api.entities.room_member import RoomMember
from backend.api.entities.room_message import RoomMessage
from backend.api.entities.user import User
from backend.api.std import sql


class RoomRepo:
    """
    RoomRepo
    チャットルーム関連のSQL処理を束ねたクラス
    """

    def find_list(
        self,
        room_name: Optional[str] = None,
        member_id: Optional[id] = None,
        offset: int = 0,
        limit: int = 10,
    ) -> Tuple[Sequence[Room], int]:
        """
        指定した条件に合致するルーム情報を取得
            Args:
                room_name: ルーム名（部分一致）
                member_name: メンバー名（部分一致）
                offset: 何件目から取得するか指定（全件表示する場合は-1を指定）
                limit: 何件取得するか指定
            Returns:
                Sequence: ヒットしたルーム情報のリスト
                int: ヒットした件数
        """
        with sql.Session() as session:
            query = select(Room)
            query = query.where(Room.del_flag == False)

            if room_name:
                query = query.where(
                    Room.room_name.contains(room_name)
                )
            if member_id:
                query = query.where(
                    Room.members.any(RoomMember.user_id == member_id)
                    )

            # 更新日で並び替え
            query = query.order_by(
                desc(Room.update_date)
            )

            # レコード件数取得
            count_query = select(func.count()).select_from(query.subquery())
            rec_count = session.execute(count_query).scalar() or 0

            # 検索処理時のみオフセット指定（Excelダウンロード時は不要）
            if offset >= 0:
                query = query.offset(offset).limit(limit)

            room_list = session.scalars(query).unique().all()

            return room_list, rec_count

    def find_by_id(self, id: int) -> Room:
        """
        指定したidのルーム情報を取得
            Args:
                id: Room のID
            Returns:
                Room: 取得したルーム情報
        """
        with sql.Session() as session:
            return (
                session.scalars(
                    select(Room).where(
                        Room.id == id
                    )
                )
                .unique()
                .one()
            )

    def find_member(self, member_id: int) -> Sequence[User]:
        '''
        指定したユーザIDが含まれるルームメンバー情報取得
                member_id: メンバーID
            Returns:
                Sequence: ヒットしたメンバのリスト
        '''

        with sql.Session() as session:
            query = select(User).distinct()
            query = query.join(RoomMember, RoomMember.user_id == User.id)
            query = query.where(
                RoomMember.room_id.in_(
                    select(RoomMember.room_id).where(RoomMember.user_id == member_id)
                )
            )
            query = query.where(RoomMember.user_id == member_id)
            
            # メールアドレスで並び替え
            query = query.order_by(asc(User.mail_address))

            return session.scalars(query).unique().all()


    def create(self, room: Room) -> int:
        """
        ルーム情報を作成
            Args:
                room: 登録対象のルーム情報クラス
            Returns:
                int: 登録したレコードのID
        """
        with sql.Session() as session:
            session.add(room)
            session.add(room.room_member)
            session.commit()
            assert room.id is not None
            return room.id

    def update(self, room: Room):
        """
        ルーム情報を更新
            Args:
                room: 更新対象のルーム情報クラス
            Returns:

        """
        with sql.Session() as session:
            current_room = (
                session.scalars(
                    select(Room).where(Room.id == room.id)
                )
                .unique()
                .one()
            )
            current_room.room_name = room.room_name
            current_room.remarks = room.remarks
            session.commit()

    def delete(self, room: Room):
        """
        ルーム情報を削除
            Args:
                room: 削除対象のルーム情報クラス
            Returns:

        """
        with sql.Session() as session:
            current_room = session.scalars(
                select(Room).where(Room.id == room.id)
            ).one()
            session.delete(current_room)
            session.commit()
