from typing import Optional, Sequence, Tuple

from sqlalchemy import and_, asc, desc, func, select

from backend.api.entities.room import Room
from backend.api.entities.room_member import RoomMember
from backend.api.entities.room_message import RoomMessage
from backend.api.entities.user import User
from backend.api.repositories.user import UserRepo
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
                query = query.where(Room.room_name.contains(room_name))
            if member_id:
                query = query.where(Room.members.any(RoomMember.user_id == member_id))

            # 更新日で並び替え
            query = query.order_by(desc(Room.update_date))

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
            return session.scalars(select(Room).where(Room.id == id)).unique().one()

    def find_member_by_user_id(self, room_id: int, user_id) -> Room:
        """
        指定したidのメンバ情報を取得
            Args:
                room_id: Room のID
                user_id: メンバのユーザID
            Returns:
                Room: 取得したメンバ情報
        """
        with sql.Session() as session:
            return (
                session.scalars(
                    select(RoomMember).where(
                        and_(
                            RoomMember.room_id == room_id, RoomMember.user_id == user_id
                        )
                    )
                )
                .unique()
                .first()
            )

    def find_member_in_target_user(self, member_id: int) -> Sequence[User]:
        """
        指定したユーザIDが含まれるルームメンバー情報取得
                member_id: メンバーID
            Returns:
                Sequence: ヒットしたメンバのリスト
        """

        with sql.Session() as session:
            query = select(User).distinct()
            query = query.join(RoomMember, RoomMember.user_id == User.id)
            query = query.where(
                RoomMember.room_id.in_(
                    select(RoomMember.room_id).where(RoomMember.user_id == member_id)
                )
            )

            # メールアドレスで並び替え
            query = query.order_by(asc(User.mail_address))

            return session.scalars(query).unique().all()

    def create(self, room: Room, members: list) -> int:
        """
        ルーム情報を作成
            Args:
                room: 登録対象のルーム情報クラス
                members: 登録するメンバ
            Returns:
                int: 登録したレコードのID
        """
        with sql.Session() as session:
            session.add(room)

            user_repo = UserRepo()
            for member in members:
                user = user_repo.find_by_address(member)
                if user:
                    room.members.append(RoomMember(user_id=user.id))

                else:
                    new_user = User()
                    new_user.mail_address = member
                    new_user.user_name = member
                    new_user.hashed_password = member
                    new_id = user_repo.create(new_user)
                    room.members.append(RoomMember(user_id=new_id))

            session.commit()
            assert room.id is not None
            return room.id

    def update(self, room: Room, new_members: list):
        """
        ルーム情報を更新
            Args:
                room: 更新対象のルーム情報クラス
                members: 登録するメンバ
            Returns:

        """
        with sql.Session() as session:
            current_room = (
                session.scalars(select(Room).where(Room.id == room.id)).unique().one()
            )
            current_room.room_name = room.room_name
            current_room.remarks = room.remarks

            # --- 既存のメンバアドレス情報を取得 ---
            user_repo = UserRepo()
            existing_members = []
            for member in current_room.members:
                user = user_repo.find_by_id(member.user_id)
                existing_members.append(user.mail_address)

            # --- 削除対象（既存にしかいない）---
            for member_addr in set(existing_members) - set(new_members):
                user = user_repo.find_by_address(member_addr)
                # 現在の Room.members から user_id が一致するオブジェクトを取得
                member_obj = next(
                    (m for m in current_room.members if m.user_id == user.id), None
                )
                if member_obj:
                    current_room.members.remove(member_obj)

            # --- 追加対象（新規にしかいない）---
            for member_addr in set(new_members) - set(existing_members):
                user = user_repo.find_by_address(member_addr)
                if user:
                    current_room.members.append(RoomMember(user_id=user.id))
                else:
                    new_user = User()
                    new_user.mail_address = member_addr
                    new_user.user_name = member_addr
                    new_user.hashed_password = member_addr
                    new_id = user_repo.create(new_user)
                    current_room.members.append(RoomMember(user_id=new_id))

            session.commit()

    def delete(self, room: Room):
        """
        ルーム情報を削除
            Args:
                room: 削除対象のルーム情報クラス
            Returns:

        """
        with sql.Session() as session:
            current_room = session.scalars(select(Room).where(Room.id == room.id)).one()
            session.delete(current_room)
            session.commit()
