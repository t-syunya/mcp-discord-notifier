.PHONY: help format lint type-check check all mcp mcp-bot voicevox start-all

help:
	@echo "利用可能なコマンド:"
	@echo "  make format      - Ruff でコードをフォーマット"
	@echo "  make lint        - Ruff でリントチェック"
	@echo "  make type-check  - Ty で型チェック"
	@echo "  make check       - format, lint, type-check を順次実行"
	@echo "  make all         - check のエイリアス"
	@echo "  make mcp         - MCPサーバー(mcp-discord-notifier)を起動"
	@echo "  make mcp-bot     - Botデーモン(Discord + VoiceVox連携)を起動"
	@echo "  make voicevox    - VoiceVox Engine を docker-compose で起動"
	@echo "  make start-all   - VoiceVox + Botデーモン + MCPサーバーを一括起動"

format:
	@echo "🎨 Ruff フォーマットを実行中..."
	uv run --group dev ruff format --config pyproject.toml .

lint:
	@echo "🔍 Ruff リントチェックを実行中..."
	uv run --group dev ruff check .

type-check:
	@echo "📝 Ty 型チェックを実行中..."
	PYTHONPATH=src uv run --group dev ty check src/

check: format lint type-check
	@echo "✅ すべてのチェックが完了しました"

all: check

# 共通: .env を読み込み、UV_CACHE_DIR をリポジトリ配下に固定
MCP_ENV = set -a; [ -f .env ] && source .env; set +a; \
	UV_CACHE_DIR=$$(pwd)/.uv-cache

mcp:
	@echo "🚀 MCPサーバー (mcp-discord-notifier) を uv 経由で起動します..."
	@$(MCP_ENV); UV_CACHE_DIR=$$UV_CACHE_DIR uv run mcp-discord-notifier --log-thread-name "$${LOG_THREAD_NAME:-Conversation Log}"

mcp-bot:
	@echo "🎧 Discord Bot デーモン (VoiceVox対応) を uv 経由で起動します..."
	@$(MCP_ENV); UV_CACHE_DIR=$$UV_CACHE_DIR uv run mcp-discord-bot-daemon

voicevox:
	@echo "🔊 VoiceVox Engine を docker-compose で起動します..."
	@$(MCP_ENV); UV_CACHE_DIR=$$UV_CACHE_DIR docker-compose up -d voicevox

start-all:
	@echo "🌐 VoiceVox + Botデーモン + MCPサーバーを一括起動します..."
	@$(MCP_ENV); \
	UV_CACHE_DIR=$$UV_CACHE_DIR docker-compose up -d voicevox && \
	echo "🎧 Bot Daemon をバックグラウンド起動 (PIDを /tmp/mcp-bot.pid に保存)" && \
	UV_CACHE_DIR=$$UV_CACHE_DIR uv run mcp-discord-bot-daemon > /tmp/mcp-bot.log 2>&1 & echo $! > /tmp/mcp-bot.pid && \
	echo "🚀 MCP Server をバックグラウンド起動 (PIDを /tmp/mcp-server.pid に保存)" && \
	UV_CACHE_DIR=$$UV_CACHE_DIR uv run mcp-discord-notifier --log-thread-name "$${LOG_THREAD_NAME:-Conversation Log}" > /tmp/mcp-server.log 2>&1 & echo $! > /tmp/mcp-server.pid && \
	echo "✅ 起動完了: logs=/tmp/mcp-bot.log, /tmp/mcp-server.log"
