from typing import Sequence

from sqlalchemy import and_, select

from api.entities.category import Category
from api.std import sql


class CategoryRepo:
    """
    CategoryRepo
    カテゴリマスタへのSQL処理を束ねたクラス
    """

    def list(self) -> Sequence[Category]:
        """
        カテゴリのリストを取得
            Args:
            Returns:
                Sequence: 取得したカテゴリのリスト
        """
        with sql.Session() as session:
            return session.scalars(
                select(Category)
                .where(and_(Category.del_flag == False, Category.maintenance_flag == True))
                .order_by(Category.sort_key)
            ).all()
