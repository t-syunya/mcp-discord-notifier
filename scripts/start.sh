#!/bin/bash

# MCP Discord Notifier - Start Script
# このスクリプトは、VoiceVoxとMCPサーバーを起動します

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "=========================================="
echo "  MCP Discord Notifier - Start Script"
echo "=========================================="
echo ""

# 色の定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# .envファイルの確認と読み込み
echo -e "${BLUE}[1/4] 設定ファイルをチェックしています...${NC}"

if [ -f ".env" ]; then
    echo -e "${GREEN}  ✓ .env ファイルが見つかりました${NC}"
    # .env ファイルを読み込み（既に環境変数が設定されている場合は上書きしない）
    set -a
    source .env
    set +a
else
    echo -e "${YELLOW}  ⚠ .env ファイルが見つかりません${NC}"
    echo ""
    echo -e "${RED}.env ファイルを作成してください。${NC}"
    echo ""
    echo "以下のコマンドでサンプルファイルをコピーできます："
    echo ""
    echo "  cp .env.example .env"
    echo ""
    echo "その後、.env ファイルを編集して必要な値を設定してください。"
    echo ""
    exit 1
fi

# 必須の環境変数チェック
MISSING_VARS=0

if [ -z "$DISCORD_TOKEN" ]; then
    echo -e "${YELLOW}  ⚠ DISCORD_TOKEN が設定されていません${NC}"
    MISSING_VARS=1
fi

if [ -z "$LOG_CHANNEL_ID" ]; then
    echo -e "${YELLOW}  ⚠ LOG_CHANNEL_ID が設定されていません${NC}"
    MISSING_VARS=1
fi

if [ $MISSING_VARS -eq 1 ]; then
    echo ""
    echo -e "${RED}.env ファイルに必須の設定が不足しています。${NC}"
    echo ""
    echo ".env ファイルを編集して以下の項目を設定してください："
    echo ""
    echo "  DISCORD_TOKEN=your-discord-bot-token"
    echo "  LOG_CHANNEL_ID=your-channel-id"
    echo ""
    exit 1
fi

echo -e "${GREEN}  ✓ 設定の確認完了${NC}"
echo ""

# VoiceVoxの起動確認
echo -e "${BLUE}[2/4] VoiceVox Engine を起動しています...${NC}"

if command -v docker-compose &> /dev/null || command -v docker &> /dev/null; then
    if docker-compose ps | grep -q voicevox; then
        echo -e "${GREEN}  ✓ VoiceVox Engine は既に起動しています${NC}"
    else
        echo "  VoiceVox Engine を起動中..."
        docker-compose up -d

        # 起動待機
        echo "  起動を待機しています（最大30秒）..."
        COUNTER=0
        while [ $COUNTER -lt 30 ]; do
            if curl -s http://localhost:50021/version > /dev/null 2>&1; then
                echo -e "${GREEN}  ✓ VoiceVox Engine が起動しました${NC}"
                break
            fi
            sleep 1
            COUNTER=$((COUNTER + 1))
        done

        if [ $COUNTER -eq 30 ]; then
            echo -e "${YELLOW}  ⚠ VoiceVox Engine の起動確認がタイムアウトしました${NC}"
            echo -e "${YELLOW}  　音声通知は失敗します。VoiceVox を起動して再試行してください${NC}"
        fi
    fi
else
    echo -e "${YELLOW}  ⚠ Docker がインストールされていません${NC}"
    echo -e "${YELLOW}  　VoiceVox Engine を起動できないため音声通知は失敗します${NC}"
fi
echo ""

# FFmpegの確認
echo -e "${BLUE}[3/4] FFmpeg を確認しています...${NC}"
if command -v ffmpeg &> /dev/null; then
    echo -e "${GREEN}  ✓ FFmpeg がインストールされています${NC}"
else
    echo -e "${YELLOW}  ⚠ FFmpeg がインストールされていません${NC}"
    echo -e "${YELLOW}  　音声再生機能を使用する場合はインストールしてください${NC}"
fi
echo ""

# Discord Bot Daemonの起動
echo -e "${BLUE}[4/4] Discord Bot Daemon を起動しています...${NC}"
echo ""
echo "設定:"
echo "  Discord Token: ${DISCORD_TOKEN:0:20}..."
echo "  Log Channel ID: $LOG_CHANNEL_ID"
echo "  Log Thread Name: ${LOG_THREAD_NAME:-Conversation Log}"
echo "  VoiceVox URL: ${VOICEVOX_URL:-http://localhost:50021}"
echo "  HTTP API: http://127.0.0.1:8765"
echo ""
echo -e "${GREEN}Bot Daemon を起動します（Ctrl+C で停止）...${NC}"
echo "=========================================="
echo ""
echo "MCP Server は別プロセスとして Claude Code が自動起動します"
echo "Bot Daemon は HTTP API (port 8765) で MCP Server からのリクエストを受け付けます"
echo ""

# PIDファイルのディレクトリを作成
mkdir -p /tmp/mcp-discord-notifier

# Bot Daemon を起動
uv run mcp-discord-bot-daemon
