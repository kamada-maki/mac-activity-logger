# PC 作業ログに基づく日報作成 指示書

あなたは私の有能な秘書です。
提供する 1 分ごとの PC 作業ログ（JSONL 形式）を分析し、今日一日の活動を振り返るための日報を作成してください。

---

## ■ ログファイルの場所と形式

- パス: `./log_YYYYMMDD.jsonl`
- 形式: JSONL（1行1レコード）
- フィールド:
  - `timestamp`: ISO 8601形式のタイムスタンプ
  - `apps`: 各ディスプレイの最前面アプリ名の配列（例: `["Chrome", "Cursor"]`）
  - `text`: OCRで読み取った画面テキスト

引数に日付がない場合は、どの日を対象とするか尋ねてください。

### appsフィールドの活用

`apps`フィールドには各ディスプレイの最前面アプリが配列で記録されている。
例: `["Chrome", "Cursor"]` → Screen 0でChrome、Screen 1でCursorを使用

**分析に活用できる情報：**
- アプリの組み合わせパターン（例: Chrome+Cursor = ドキュメント参照しながらコーディング）
- 各アプリの使用頻度（配列内の出現回数をカウント）
- 作業スタイルの傾向（1画面集中 vs 2画面並行作業）

```bash
# アプリ使用頻度（全ディスプレイ合算）
cat log_YYYYMMDD.jsonl | jq -r '.apps[]' | sort | uniq -c | sort -rn

# アプリの組み合わせパターン
cat log_YYYYMMDD.jsonl | jq -r '.apps | sort | join(" + ")' | sort | uniq -c | sort -rn | head -10
```

### スリープ時のレコード除外

以下の条件に該当するレコードは、PCがスリープ状態のためカウントしない：
- `text`が空文字列（`""`）の場合
- `text`が「画面スリープのため作業カウントしない」の場合

```bash
# スリープ時を除外してレコード数をカウント
cat log_YYYYMMDD.jsonl | jq -r 'select(.text != "" and .text != "画面スリープのため作業カウントしない") | .timestamp' | wc -l
```

### ファイルサイズに関する注意

- 1日分のログは **1〜2MB以上** になることが多く、Readツールでは直接読めない
- **Bashコマンド（jq, grep, head, tail等）で処理すること**
- 傾向分析には全レコードの統計が必要（アプリ切り替え回数、時間帯別分布等）
- 統計コマンドで全体を集計し、詳細確認が必要な時間帯はサンプリングで補完する

---

## ■ 分析手順（効率的に処理するため）

1. **時間範囲の確認**: ログの最初と最後のタイムスタンプを取得
2. **有効レコード数の確認**: スリープ時を除外した実作業時間を算出
3. **時間帯別サンプリング**: 各時間帯の代表的なログを抽出（textフィールドから作業内容を読み取る）
4. **キーワード抽出**: ファイル名、プロジェクト名、URLなどをtextフィールドから抽出
5. **日報作成**: 上記をもとに構造化された日報を生成

```bash
# 推奨コマンド例
# 時間範囲
head -1 log_YYYYMMDD.jsonl | jq -r '.timestamp'
tail -1 log_YYYYMMDD.jsonl | jq -r '.timestamp'

# 有効レコード数（スリープ除外）
cat log_YYYYMMDD.jsonl | jq -r 'select(.text != "" and .text != "画面スリープのため作業カウントしない") | .timestamp' | wc -l

# 時間帯別レコード数（スリープ除外）
cat log_YYYYMMDD.jsonl | jq -r 'select(.text != "" and .text != "画面スリープのため作業カウントしない") | .timestamp[11:13]' | sort | uniq -c

# ファイル名抽出
cat log_YYYYMMDD.jsonl | jq -r '.text' | grep -oE "[a-zA-Z0-9_-]+\.(ts|tsx|js|py|md)" | sort | uniq -c | sort -rn | head -20

# URL抽出
cat log_YYYYMMDD.jsonl | jq -r '.text' | grep -oE "https?://[a-zA-Z0-9./?=_-]+" | sort | uniq -c | sort -rn | head -20

# ツール名の出現回数（textから抽出）
cat log_YYYYMMDD.jsonl | jq -r '.text' | grep -oE "(Slack|Notion|GitHub|Figma|DBeaver|Linear)" | sort | uniq -c | sort -rn

# アプリ使用頻度（appsフィールドから）
cat log_YYYYMMDD.jsonl | jq -r '.apps[]' | sort | uniq -c | sort -rn

# アプリの組み合わせパターン
cat log_YYYYMMDD.jsonl | jq -r '.apps | sort | join(" + ")' | sort | uniq -c | sort -rn | head -10
```

---

## ■ 出力構成

### 1. 今日一日の要約
- どのような一日だったか
- 2〜3 文で全体を総括

---

### 2. タイムライン別の活動内容

```
[開始時間 - 終了時間] タスク名
・具体的な作業内容（OCRテキストから読み取る）
・画面から読み取れるコンテキスト
```

※ 同じ作業は 1 つのタスクにまとめる
※ 使用アプリは`apps`フィールドとOCRテキストの両方を参考にする

---

### 3. 集中していたポイント・成果
- 長時間取り組んでいたこと
- 形になったもの・完了したこと

---

### 4. 学び・調べていたこと
- ブラウザ履歴や資料内容から
- 今日得た知識、直面していた課題の推測

---

### 5. 明日への引き継ぎ
- 未完了と思われること
- 次にやるべきことの提案

---

### 6. 行動の癖や傾向

以下の観点で分析し、気づきを記載してください（※OCRテキストから読み取れる範囲で）：

**作業パターン**
- 集中しやすい時間帯 / 散漫になりやすい時間帯
- 1つのタスクへの連続集中時間
- スリープ（離席）が多い時間帯

**コミュニケーション傾向**
- Slackの使用タイミングと頻度（textにSlackが含まれるレコードから推測）
- 作業中断のパターン

**開発スタイル**
- ドキュメント参照の頻度（Notion, Figma等の出現から推測）
- デバッグツール（DBeaver等）の使用パターン
- GitHub/PRレビューの頻度

**改善の示唆**
- 効率化できそうなポイント
- 注意が必要な傾向（気が散りやすい時間帯など）

---

## ■ 制約

- 同じ作業が続いている時間は 1 タスクに要約
- 「13:00 開いた / 13:01 開いた」のような分単位の羅列は禁止
- 意味のある作業単位でまとめること
- 全体の傾向や共通項などあれば、それも含めて記載すること

---

## ■ 日報の保存

作成した日報は以下のルールで保存すること：

- 保存先: `./daily-report/YYYY-MM/YYYYMMDD.md`
- 例: 2026年1月6日の日報 → `daily-report/2026-01/20260106.md`
- ディレクトリが存在しない場合は作成する

```bash
# ディレクトリ作成例
mkdir -p ./daily-report/2026-01
```

---

## ■ 古いログの圧縮

日報作成後、1週間以上前のログファイル（.jsonl）が残っていたら gzip で圧縮すること。

**ルール：**
- 対象: 7日以上前の `log_YYYYMMDD.jsonl` ファイル
- 圧縮後: `log_YYYYMMDD.jsonl.gz` になり、元ファイルは削除される
- 圧縮済み（.gz）ファイルは削除しない

```bash
# 1週間以上前のログを圧縮するコマンド（リポジトリルートで実行）
find . -maxdepth 1 -name "log_*.jsonl" -mtime +7 -exec gzip {} \;
```

**確認用：**
```bash
# 未圧縮のログファイル一覧
ls -la ./log_*.jsonl 2>/dev/null

# 圧縮済みログファイル一覧
ls -la ./log_*.jsonl.gz 2>/dev/null
```
