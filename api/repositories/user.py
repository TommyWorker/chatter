from typing import Optional, Sequence, Tuple

from sqlalchemy import func, select

from api.entities.user import User
from api.std import sql


class UserRepo:
    """
    UserRepo
    ユーザマスタへのSQL処理を束ねたクラス
    """

    def find(
        self,
        mail_address: Optional[str] = None,
        user_name: Optional[str] = None,
        offset: int = 0,
        limit: int = 10,
    ) -> Tuple[Sequence[User], int]:
        """
        指定した条件に合致するユーザを取得
            Args:
                mail_address: メールアドレス（部分一致）
                user_name: 名前（部分一致）
                offset: 何件目から取得するか指定（全件表示する場合は-1を指定）
                limit: 何件取得するか指定
            Returns:
                Sequence: ヒットしたユーザ情報のリスト
                int: ヒットした件数
        """
        with sql.Session() as session:

            query = select(User)
            if mail_address:
                query = query.where(User.mail_address.contains(mail_address))
            if user_name:
                query = query.where(User.user_name.contains(user_name))
            # query = query.where(User.del_flag == 0)
            query = query.order_by(User.del_flag, User.user_name)

            # レコード件数取得
            count_query = select(func.count()).select_from(query.subquery())
            rec_count = session.execute(count_query).scalar() or 0

            # オフセット指定
            if offset >= 0:
                query = query.offset(offset).limit(limit)

            # 検索実施
            user_list = session.scalars(query).unique().all()

            return user_list, rec_count

    def find_by_id(self, id: int) -> User:
        """
        指定したアカウントコードのユーザを取得
            Args:
                id: ユーザID
            Returns:
                User: 取得したユーザ情報
        """
        with sql.Session() as session:
            return session.scalars(select(User).where(User.id == id)).unique().one()

    def find_by_address(self, mail_address: str) -> User:
        """
        指定したメールドレスのユーザを取得
            Args:
                address: メールドレス
            Returns:
                User: 取得したユーザ情報
        """
        with sql.Session() as session:
            return session.scalars(
                select(User).where(User.mail_address == mail_address)
            ).first()

    def create(self, user: User) -> int:
        """
        ユーザ情報を作成
            Args:
                user: 登録対象のユーザ情報クラス
            Returns:
                int: 登録したレコードのID
        """
        with sql.Session() as session:
            session.add(user)
            session.commit()
            assert user.id is not None
            return user.id

    def update(self, user: User):
        """
        ユーザ情報を更新
            Args:
                user: 更新対象のユーザ情報クラス
            Returns:

        """
        with sql.Session() as session:
            current_user = (
                session.scalars(select(User).where(User.id == user.id)).unique().one()
            )
            current_user.update_user = user.update_user
            current_user.mail_address = user.mail_address
            current_user.user_name = user.user_name
            if user.hashed_password != "":
                current_user.hashed_password = user.hashed_password
            current_user.authority_code = user.authority_code
            current_user.del_flag = user.del_flag

            session.commit()

    def delete(self, user: User):
        """
        ユーザ情報を削除
            Args:
                user: 削除対象のユーザ情報クラス
            Returns:

        """
        with sql.Session() as session:
            current_user = session.scalars(select(User).where(User.id == user.id)).one()
            session.delete(current_user)
            session.commit()
