# ChatterApp

> FastAPI と SQLAlchemy(PostgreSQL) で作ったリアルタイムチャットアプリ

---

## 目次
- [概要](#概要)
- [機能](#機能)
- [環境](#環境)
- [セットアップ](#セットアップ)
- [使い方](#使い方)
- [ディレクトリ構成](#ディレクトリ構成)
- [開発に貢献](#開発に貢献)
- [ライセンス](#ライセンス)

---

## 概要
このプロジェクトは、FastAPI と SQLAlchemy(PostgreSQL) を使って作成したリアルタイムチャットアプリです。  
ユーザー登録、ログイン、複数ルームでのチャットが可能です。

---

## 機能
- ユーザー登録・ログイン・ログアウト
- ルーム作成・メンバー追加・削除
- メッセージ送信・履歴取得
- 管理者によるメンテナンス機能

---

## 環境
- Python 3.13
- FastAPI
- SQLAlchemy 2.x
- PostgreSQL
- uvicorn
- その他ライブラリは `requirements.txt` を参照

---

## セットアップ

### 1. リポジトリをクローン
```
git clone https://xxxxxxxxxxxxx
cd chatter
```

### 2. 仮想環境を作成
```
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
```

### 3. 必要なライブラリをインストール
```
pip install -r requirements.txt
```

### 4. 環境変数を設定
ルートフォルダ直下へ.envファイルを格納し、以下の変数をセット
```
# DB 接続情報
DB_SERVER = ""
DB_DATABASE = ""
DB_PORT = ""
DB_USER = ""
DB_PW = ""

# Web 環境情報
HOST = ""     # 127.0.0.1
PORT = ""     # 80

# ミドルウェア用セッションキー（32桁程度のランダム文字列）
SESSION_KEY = ""

# 本番環境か開発環境か（prd：本番 dev：開発）
APP_ENV = ""
```

### 5. データベースを作成
PostgreSQLへアプリ用の空のDBとユーザを作成する（環境変数と合わせる）

---

## 使い方

### アプリ起動
```
uvicorn app.main:app --reload
```
ブラウザで [http://localhost:8000](http://localhost:8000) にアクセス

### DBの初期化
[http://localhost:8000/init_database](http://localhost:8000/init_database)にアクセスして画面の案内に従って初期化実施（環境変数のAPP_ENVを"dev"にしておく必要あり）

---

## ディレクトリ構成
```
chatter/
├─ api/
│  ├─ entities/            # SQLAlchemy モデル
│  ├─ repositories/        # DB操作
│  ├─ routers/             # エンドポイント
│  ├─ services/            # ロジック
│  ├─ repositories/        # DB操作
│  └─ std/                 # 共通処理
├─ data/                   # 初期データ
├─ ui/                     # マイグレーション
│  ├─ static/              # css,js,icon
│  └─ templates/           # jinja2 HTMLテンプレート
├─ Docker.py               # Dockerファイル
├─ exceptions.py           # 例外処理
├─ main.py                 # FastAPI アプリ本体
├─ requirements.txt
└─ README.md
```

---


