# ベースイメージ指定
FROM python:3.13-slim-bullseye

# OSパッケージを更新して不要キャッシュを削除
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# 作業ディレクトリ指定
WORKDIR /chatter

# 非rootユーザー作成 & 権限変更
RUN useradd -m appuser
USER appuser

# プログラムファイルをコピー
COPY --chown=appuser:appuser ./requirements.txt /chatter/requirements.txt
COPY --chown=appuser:appuser ./api /chatter/api
COPY --chown=appuser:appuser ./ui /chatter/ui
COPY --chown=appuser:appuser ./data /chatter/data
COPY --chown=appuser:appuser ./main.py /chatter/main.py

# PIPを最新化してrequirementsからインストール実施
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r /chatter/requirements.txt

# サービス起動
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
