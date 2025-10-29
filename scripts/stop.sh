#!/bin/bash

# MCP Discord Notifier - Stop Script
# このスクリプトは、MCPサーバーとVoiceVoxを停止します

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "  MCP Discord Notifier - Stop Script"
echo "=========================================="
echo ""

# 色の定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# オプション解析
STOP_VOICEVOX=1  # デフォルトで停止
FORCE_KILL=0

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-voicevox)
            STOP_VOICEVOX=0
            shift
            ;;
        --force)
            FORCE_KILL=1
            shift
            ;;
        -h|--help)
            echo "使用方法: $0 [OPTIONS]"
            echo ""
            echo "オプション:"
            echo "  --skip-voicevox   VoiceVox Engine を停止しません（デフォルトでは停止）"
            echo "  --force           プロセスを強制終了します"
            echo "  -h, --help        このヘルプを表示"
            echo ""
            exit 0
            ;;
        *)
            echo -e "${RED}不明なオプション: $1${NC}"
            echo "使用方法: $0 [--skip-voicevox] [--force] [-h]"
            exit 1
            ;;
    esac
done

# MCPサーバープロセスの停止
echo -e "${BLUE}[1/2] MCP Discord Notifier プロセスを停止しています...${NC}"

# mcp-discord-notifier プロセスを検索
PIDS=$(pgrep -f "mcp-discord-notifier" || true)

if [ -z "$PIDS" ]; then
    echo -e "${YELLOW}  ⚠ 実行中のMCP Discord Notifierプロセスが見つかりません${NC}"
else
    echo "  以下のプロセスを停止します:"
    ps -p $PIDS -o pid,cmd --no-headers | sed 's/^/    /'
    echo ""

    if [ $FORCE_KILL -eq 1 ]; then
        echo "  プロセスを強制終了しています..."
        kill -9 $PIDS
        echo -e "${GREEN}  ✓ プロセスを強制終了しました${NC}"
    else
        echo "  プロセスに終了シグナルを送信しています..."
        kill $PIDS

        # プロセスが終了するまで待機（最大10秒）
        COUNTER=0
        while [ $COUNTER -lt 10 ]; do
            if ! pgrep -f "mcp-discord-notifier" > /dev/null 2>&1; then
                echo -e "${GREEN}  ✓ プロセスが正常に終了しました${NC}"
                break
            fi
            sleep 1
            COUNTER=$((COUNTER + 1))
        done

        if [ $COUNTER -eq 10 ]; then
            echo -e "${YELLOW}  ⚠ プロセスが終了しませんでした（強制終了中）${NC}"
            kill -9 $PIDS
            echo -e "${GREEN}  ✓ プロセスを強制終了しました${NC}"
        fi
    fi
fi
echo ""

# VoiceVoxの停止
echo -e "${BLUE}[2/2] VoiceVox Engine の状態を確認しています...${NC}"

if [ $STOP_VOICEVOX -eq 1 ]; then
    if command -v docker-compose &> /dev/null || command -v docker &> /dev/null; then
        if docker-compose ps | grep -q voicevox; then
            echo "  VoiceVox Engine を停止しています..."
            docker-compose stop voicevox
            echo -e "${GREEN}  ✓ VoiceVox Engine を停止しました${NC}"

            # コンテナを削除するか確認
            read -p "  コンテナを削除しますか？ (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                docker-compose down
                echo -e "${GREEN}  ✓ VoiceVox Engine コンテナを削除しました${NC}"
            fi
        else
            echo -e "${YELLOW}  ⚠ VoiceVox Engine は実行されていません${NC}"
        fi
    else
        echo -e "${YELLOW}  ⚠ Docker がインストールされていません${NC}"
    fi
else
    if command -v docker-compose &> /dev/null && docker-compose ps | grep -q voicevox; then
        echo -e "${GREEN}  ✓ VoiceVox Engine は実行中です（停止をスキップします）${NC}"
        echo -e "${YELLOW}  　--skip-voicevox オプションが指定されています${NC}"
    else
        echo -e "${YELLOW}  ⚠ VoiceVox Engine は実行されていません${NC}"
    fi
fi
echo ""

echo "=========================================="
echo -e "${GREEN}停止処理が完了しました${NC}"
echo "=========================================="
