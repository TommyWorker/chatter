from typing import Optional, Sequence, Tuple, Dict

from backend.api.entities.room import Room
from backend.api.entities.room_member import RoomMember
from backend.api.entities.room_message import RoomMessage
from backend.api.entities.user import User
from backend.api.repositories.room import RoomRepo
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
    

def get_selected_lists(login_user_id: id) -> Dict[str, Sequence[User]]:
    """
    画面の選択項目のリスト取得
        Args:

        Returns:
            以下のリストを返す辞書
                member: メンバーリスト
    """

    room_repo = RoomRepo()

    member_list = room_repo.find_member(login_user_id)

    return {
        "member": member_list,
    }
