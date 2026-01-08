#!/bin/bash
cd "$(dirname "$0")"

echo "ログ記録を開始します（Ctrl+Cで停止→日報作成）"
python3 logger.py

# 停止後、自動で日報作成
DATE=$(date +%Y%m%d)
echo ""
echo "日報を作成しています..."
claude -p "/daily-report $DATE"
