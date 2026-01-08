# Mac Activity Logger

1 分ごとに Mac の画面をキャプチャし、標準の Vision Framework で OCR（文字起こし）を行い、作業内容を JSONL 形式で保存するツールです。

## 概要

- ローカル完結：OCR 処理はすべて Mac 内で完結し、外部にデータが送信されません。
- 軽量：画像は OCR 後に即座に削除され、テキストのみを蓄積します。
- マルチディスプレイ対応：複数画面それぞれの最前面アプリを記録します。
- 日報自動作成：ログ停止時に Claude Code で自動的に日報を生成します。

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

作業を開始する際の起動手順です。

### プログラムの起動（日報自動作成あり）

ターミナルを開き、以下のコマンドを実行します。停止時に自動で日報が作成されます。

```bash
cd ~/git/mac-activity-logger && source venv/bin/activate && ./start-logging.sh
```

### プログラムの起動（ログ収集のみ）

日報作成なしでログ収集のみ行う場合：

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

- logger.py：ログ収集プログラム
- start-logging.sh：起動スクリプト（停止時に日報自動作成）
- log_YYYYMMDD.jsonl：日次の作業ログ
- daily-report/：生成された日報の保存先
- .claude/commands/daily-report.md：Claude Code 用の日報作成コマンド
- venv/：Python の実行環境（Git 管理対象外）
- .gitignore：ログファイルや一時画像を Git に含めないための設定

## 5. 日報自動作成について

日報自動作成機能を使うには [Claude Code](https://claude.ai/code) のインストールが必要です。

```bash
# Claude Code のインストール
npm install -g @anthropic-ai/claude-code
```

日報は `daily-report/YYYY-MM/YYYYMMDD.md` に保存されます。
