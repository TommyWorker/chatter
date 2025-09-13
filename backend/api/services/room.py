from typing import Dict, Optional, Sequence, Tuple

from backend.api.entities.room import Room
from backend.api.entities.room_member import RoomMember
from backend.api.entities.room_message import RoomMessage
from backend.api.entities.user import User
from backend.api.repositories.room import RoomRepo
from backend.api.repositories.user import UserRepo
from backend.api.std import func


def find_rooms(
    room_name: Optional[str] = None,
    member_id: Optional[id] = None,
    offset: int = 0,
    limit: int = 10,
) -> Tuple[Sequence[Room], int]:
    """
    ルーム情報一覧取得処理
    Args:
        room_name: ルーム名（部分一致）
        member_name: メンバー名（部分一致）
        offset: 何件目から取得するか指定（全件表示する場合は-1を指定）
        limit: 何件取得するか指定
    Returns:
        list: 検索結果のリスト
        int: レコード件数
    """
    room_repo = RoomRepo()
    return room_repo.find_list(room_name, member_id, offset, limit)


def get_room(id: int) -> Room:
    """
    ルーム情報取得
        Args:
            id: ユーザID
        Returns:
            Room: 取得したルーム情報
    """

    # ルームクラスのインスタンス生成
    if id == 0:
        return Room()
    else:
        room_repo = RoomRepo()
        return room_repo.find_by_id(id)


def get_member_by_mail(mail_address: str) -> User:
    """
    アドレスからメンバ情報取得
        Args:
            mail_address: メールアドレス
        Returns:
            User: 取得したメンバ情報
    """

    user_repo = UserRepo()
    user = user_repo.find_by_address(mail_address)
    if not user:
        user = User()
        user.user_name = mail_address
        user.mail_address = mail_address
        user.hashed_password = mail_address
        user.authority_code = 0
        user_id = user_repo.create(user)
        user = user_repo.find_by_id(user_id)
    return user


def get_selected_lists(login_user_id: id) -> Dict[str, Sequence[User]]:
    """
    画面の選択項目のリスト取得
        Args:

        Returns:
            以下のリストを返す辞書
                member: メンバーリスト
    """

    room_repo = RoomRepo()

    member_list = room_repo.find_member_in_target_user(login_user_id)

    return {
        "members": member_list,
    }


def create_room(room: Room, members: list) -> Room:
    """
    ルーム情報 新規登録
        Args:
            room: 登録するルーム情報
        Returns:
            Room: 登録したルーム情報
    """

    room_repo = RoomRepo()
    room_id = room_repo.create(room, members)
    return room_repo.find_by_id(room_id)


def update_room(room: Room, members: list) -> Room:
    """
    ルーム情報 更新
        Args:
            room: 更新するルーム情報
        Returns:
            room: 更新したルーム情報

    """

    room_repo = RoomRepo()
    room_repo.update(room, members)
    assert room.id is not None
    return room_repo.find_by_id(room.id)


def entry_message(room_message: RoomMessage):
    """
    メッセージ登録
        Args:
            room_message: メッセージ情報
        Returns:

    """
    room_repo = RoomRepo()
    room_repo.entry_message(room_message)
