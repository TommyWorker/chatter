import hashlib
import sys
import traceback
from datetime import datetime

from openpyxl.styles import Font, PatternFill
from openpyxl.styles.borders import Border, Side

"""
    func.py
    機能に依存しない共通関数群
"""


def convert_format_size_func(file_size: int) -> str:
    """
    ファイルサイズに応じて単位を設定した表記用文字列を返す
    Args:
        file_size > 変換対象のファイルサイズ
    Returns:
        変換後の文字列

    """
    # 表記フォーマットを辞書で作成
    bit = {"KB": 10, "MB": 20, "GB": 30, "TB": 40}

    # 辞書のキーと値をループで順次、取得する
    for unit, bit_shift in bit.items():
        # ビット変換
        val = file_size / float(1 << bit_shift)
        if val < 1000:
            break  # 1000未満になったらループを抜ける

    return "{:,.2f}".format(val) + " " + unit


def set_sheets_orgformat(sht, is_header_exists: bool):
    """
    指定したワークシートの書式を整える
      ・データ部に罫線付与
      ・ヘッダーに背景色
      ・フォントを指定
    Args:
        sht > 変換対象のワークシート
        is_header_exists > True ヘッダーあり
    Returns:

    """
    # 黒の細線で罫線
    side_set = Side(style="thin", color="000000")
    border_set = Border(top=side_set, bottom=side_set, left=side_set, right=side_set)

    # データが入っているすべてのセル
    for row in sht.rows:
        for cell in row:
            # ヘッダがある場合はTrueにする
            if is_header_exists:
                if cell.row == 1:
                    # ヘッダー行の色変更
                    cell.fill = PatternFill(
                        fgColor="b0c4de", bgColor="b0c4de", fill_type="solid"
                    )

                # 罫線設定
                cell.border = border_set
                # フォント設定
                sht[cell.coordinate].font = Font(name="Meiryo UI")


def get_exc_info(app_env: str = "dev") -> str:
    """
    例外情報を取得する
    Args:
        app_env > 環境情報（prd:本番、dev:開発）
    Returns:
        生成したメッセージ
    """

    exc_type, exc_value, exc_traceback = sys.exc_info()
    traceback_string = "".join(
        traceback.format_exception(exc_type, exc_value, exc_traceback)
    )

    message = (
        f"発生日時 ({datetime.now()}) をそえてシステム管理者にお問い合わせください"
    )
    if app_env == "dev":
        message = traceback_string

    return message if message is not None else ""


def convert_password(target_text: str) -> str:
    """
    パスワード文字列の暗号化
    Args:
        target_text > 変換対象の文字列
    Returns:
        変換後の文字列

    """
    return hashlib.sha256(target_text.encode()).hexdigest()
