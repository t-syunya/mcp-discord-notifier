.PHONY: help format lint type-check check all mcp mcp-bot voicevox start-all stop-all
SHELL := /bin/bash

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
	@echo "  make stop-all    - VoiceVox + Botデーモン + MCPサーバーをまとめて停止"

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
DOCKER_COMPOSE := $(shell if command -v docker-compose >/dev/null 2>&1; then echo "docker-compose"; elif command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then echo "docker compose"; fi)

mcp:
	@echo "🚀 MCPサーバー (mcp-discord-notifier) を uv 経由で起動します..."
	@$(MCP_ENV); UV_CACHE_DIR=$$UV_CACHE_DIR uv run mcp-discord-notifier --log-thread-name "$${LOG_THREAD_NAME:-Conversation Log}"

mcp-bot:
	@echo "🎧 Discord Bot デーモン (VoiceVox対応) を uv 経由で起動します..."
	@$(MCP_ENV); UV_CACHE_DIR=$$UV_CACHE_DIR uv run mcp-discord-bot-daemon

voicevox:
	@echo "🔊 VoiceVox Engine を docker-compose で起動します..."
	@$(MCP_ENV); \
	if [ -z "$(DOCKER_COMPOSE)" ]; then \
		echo "⚠️ docker-compose / docker compose が見つかりません"; exit 1; \
	else \
		UV_CACHE_DIR=$$UV_CACHE_DIR $(DOCKER_COMPOSE) up -d voicevox; \
	fi

start-all:
	@echo "🌐 VoiceVox + Botデーモン + MCPサーバーを一括起動します..."
	@$(MCP_ENV); \
	if [ -z "$(DOCKER_COMPOSE)" ]; then \
		echo "⚠️ docker-compose / docker compose が見つかりません"; exit 1; \
	else \
		UV_CACHE_DIR=$$UV_CACHE_DIR $(DOCKER_COMPOSE) up -d voicevox; \
	fi && \
	echo "🎧 Bot Daemon をバックグラウンド起動 (PIDを /tmp/mcp-bot.pid に保存)" && \
	UV_CACHE_DIR=$$UV_CACHE_DIR uv run mcp-discord-bot-daemon > /tmp/mcp-bot.log 2>&1 & echo $! > /tmp/mcp-bot.pid && \
	echo "🚀 MCP Server をバックグラウンド起動 (PIDを /tmp/mcp-server.pid に保存)" && \
	UV_CACHE_DIR=$$UV_CACHE_DIR uv run mcp-discord-notifier --log-thread-name "$${LOG_THREAD_NAME:-Conversation Log}" > /tmp/mcp-server.log 2>&1 & echo $! > /tmp/mcp-server.pid && \
	echo "✅ 起動完了: logs=/tmp/mcp-bot.log, /tmp/mcp-server.log"

stop-all:
	@echo "🛑 VoiceVox + Botデーモン + MCPサーバーをまとめて停止します..."
	@$(MCP_ENV); \
	if [ -f /tmp/mcp-server.pid ]; then \
		PID=$$(cat /tmp/mcp-server.pid); \
		if [ -n "$$PID" ] && kill -0 $$PID 2>/dev/null; then \
			echo "🚫 MCP Server (PID $$PID) を停止します..."; \
			kill $$PID && echo "✅ MCP Server 停止完了"; \
		else \
			echo "ℹ️ MCP Server は稼働していないようです"; \
		fi; \
	else \
		echo "ℹ️ MCP Server PID ファイルが見つかりません"; \
	fi; \
	if [ -f /tmp/mcp-bot.pid ]; then \
		PID=$$(cat /tmp/mcp-bot.pid); \
		if [ -n "$$PID" ] && kill -0 $$PID 2>/dev/null; then \
			echo "🚫 Bot Daemon (PID $$PID) を停止します..."; \
			kill $$PID && echo "✅ Bot Daemon 停止完了"; \
		else \
			echo "ℹ️ Bot Daemon は稼働していないようです"; \
		fi; \
	else \
		echo "ℹ️ Bot Daemon PID ファイルが見つかりません"; \
	fi; \
	echo "🔇 VoiceVox Engine を停止します..."; \
	if [ -z "$(DOCKER_COMPOSE)" ]; then \
		echo "⚠️ docker-compose / docker compose が見つかりません"; \
	else \
		$(DOCKER_COMPOSE) stop voicevox >/dev/null && echo "✅ VoiceVox 停止完了" || echo "⚠️ VoiceVox 停止に失敗しました"; \
	fi
