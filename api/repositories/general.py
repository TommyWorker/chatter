from typing import Optional, Sequence, Tuple

from sqlalchemy import and_, func, select

from api.entities.category import Category
from api.entities.general import General
from api.std import sql


class GeneralRepo:
    """
    GeneralRepo
    汎用マスタへのSQL処理を束ねたクラス
    """

    def find(self, category: str) -> Sequence[General]:
        """
        指定したカテゴリのリストを取得
            Args:
                category: 汎用マスタ上のカテゴリを指定
            Returns:
                Sequence: 指定したコード情報のリスト
        """
        with sql.Session() as session:
            return (
                session.scalars(
                    select(General)
                    .where(and_(General.category == category, General.del_flag == False))
                    .order_by(General.sort_key)
                )
                .unique()
                .all()
            )

    def find_list(
        self,
        category: Optional[str] = None,
        code_value: Optional[str] = None,
        offset: int = 0,
        limit: int = 10,
    ) -> Tuple[Sequence[General], int]:
        """
        指定した条件に合致する汎用マスタ情報を取得
            Args:
                category: カテゴリ（完全一致）
                code_value: 名称（部分一致）
                offset: 何件目から取得するか指定（全件表示する場合は-1を指定）
                limit: 何件取得するか指定
            Returns:
                Sequence: ヒットした汎用マスタ情報のリスト
                int: ヒットした件数
        """
        with sql.Session() as session:
            query = select(General)
            query = query.outerjoin(Category)
            query = query.where(Category.maintenance_flag == True)

            if category:
                query = query.where(General.category == category)
            if code_value:
                query = query.where(General.code_value.contains(code_value))

            # カテゴリ、ソートキー、削除フラグで並び替え
            query = query.order_by(
                Category.display_name, General.del_flag, General.sort_key
            )

            # レコード件数取得
            count_query = select(func.count()).select_from(query.subquery())
            rec_count = session.execute(count_query).scalar() or 0

            # 検索処理時のみオフセット指定（Excelダウンロード時は不要）
            if offset >= 0:
                query = query.offset(offset).limit(limit)

            general_list = session.scalars(query).unique().all()

            return general_list, rec_count

    def find_by_code(self, code: int, category: str) -> General:
        """
        指定したcode,categoryの汎用マスタ情報を取得
            Args:
                code: 汎用マスタコード
                category: 値
            Returns:
                General: 取得した汎用マスタ情報
        """
        with sql.Session() as session:
            return (
                session.scalars(
                    select(General).where(
                        General.code == code, General.category == category
                    )
                )
                .unique()
                .one()
            )

    def create(self, general: General) -> int:
        """
        機種情報を作成
            Args:
                general: 登録対象の汎用マスタ情報クラス
            Returns:
                int: 登録したレコードのID
        """

        with sql.Session() as session:
            max_value = (
                session.query(func.max(General.code) + 1)
                .filter(General.category == general.category)
                .scalar()
            )
            general.code = max_value
            session.add(general)
            session.commit()
            return general.code

    def update(self, general: General):
        """
        機種情報を更新
            Args:
                general: 更新対象の汎用マスタ情報クラス
            Returns:

        """
        with sql.Session() as session:
            current_general = (
                session.scalars(
                    select(General).where(
                        General.code == general.code,
                        General.category == general.category,
                    )
                )
                .unique()
                .one()
            )
            current_general.category = general.category
            current_general.code = general.code
            current_general.code_value = general.code_value
            current_general.sort_key = general.sort_key
            current_general.remarks = general.remarks
            current_general.del_flag = general.del_flag
            session.commit()

    def duplicate_check(self, general: General) -> bool:
        """
        同カテゴリ内の同一の名称の有無のチェック
            Args:
                general: 重複チェック対象の汎用関連情報
            Returns:
                bool: 重複データが0件の場合はtrue
        """
        with sql.Session() as session:
            query = select(func.count()).where(
                General.category == general.category,
                General.code_value == general.code_value,
                General.code != general.code,
            )
            result = session.execute(query).scalar()
        return result == 0
