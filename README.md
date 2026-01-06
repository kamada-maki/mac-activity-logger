# Mac Activity Logger

1 分ごとに Mac の画面をキャプチャし、標準の Vision Framework で OCR（文字起こし）を行い、作業内容を JSONL 形式で保存するツールです。

## 概要

- ローカル完結：OCR 処理はすべて Mac 内で完結し、外部にデータが送信されません。
- 軽量：画像は OCR 後に即座に削除され、テキストのみを蓄積します。
- AI 連携：保存されたログを AI（ChatGPT や Claude 等）に渡すことで、日報作成を自動化できます。

## 1. 初回セットアップ手順

プロジェクトを初めて動かす時のみ、以下の手順を実行します。

```bash
# プロジェクトフォルダへ移動
cd ~/git/mac-activity-logger

# 仮想環境（venv）の作成
python3 -m venv venv

# 仮想環境を有効化
source venv/bin/activate

# 必要なライブラリのインストール
pip install pyobjc-framework-Quartz pyobjc-framework-Vision

```

## 2. 毎日の起動・実行手順

作業を開始する際の手動起動手順です。

### プログラムの起動

ターミナルを開き、以下のコマンドを実行します。

```bash
cd ~/git/mac-activity-logger && source venv/bin/activate && python logger.py

```

### 権限の許可

初回実行時や設定リセット後に画面収録の許可を求められた場合は、以下の設定を行ってください。

1. システム設定 ＞ プライバシーとセキュリティ ＞ 画面収録 を開く。
2. 使用しているターミナル（Terminal.app や iTerm2）を ON にする。
3. プログラムを Ctrl + C で一度止め、再度上記の起動コマンドを実行する。

## 3. 動作確認と停止

### 記録の確認

別のターミナルウィンドウで以下のコマンドを実行すると、現在のログをリアルタイムで確認できます。

```bash
tail -f ~/git/mac-activity-logger/log_$(date +%Y%m%d).jsonl

```

### 停止

記録を終了したいときは、実行中のターミナルで以下を入力します。

- Ctrl + C

## 4. ファイル構成

- logger.py：メインプログラム
- log_YYYYMMDD.jsonl：日次の作業ログ
- venv/：Python の実行環境（Git 管理対象外）
- .gitignore：ログファイルや一時画像を Git に含めないための設定

## 5. 注意事項

- セキュリティ：画面上のテキストを抽出するため、パスワードや個人情報が画面に表示されている場合も記録されます。ログファイルの取り扱いには注意してください。
