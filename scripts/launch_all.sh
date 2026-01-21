#!/usr/bin/env bash
# One-shot launcher: VoiceVox + Discord Bot Daemon + MCP server

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

RUN_DIR="$PROJECT_ROOT/.run"
LOG_DIR="$PROJECT_ROOT/.logs"
UV_CACHE_DIR="$PROJECT_ROOT/.uv-cache"
DOCKER_COMPOSE_BIN=""

mkdir -p "$RUN_DIR" "$LOG_DIR"

log() { printf '[info] %s\n' "$*"; }
warn() { printf '[warn] %s\n' "$*" >&2; }
err() { printf '[error] %s\n' "$*" >&2; exit 1; }

# .env を読み込み（存在しない場合はスキップ）
set -a
[ -f "$PROJECT_ROOT/.env" ] && source "$PROJECT_ROOT/.env"
set +a

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || err "$1 が見つかりません。インストールしてください。"
}

detect_compose() {
  if command -v docker-compose >/dev/null 2>&1; then
    DOCKER_COMPOSE_BIN="docker-compose"
  elif command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
    DOCKER_COMPOSE_BIN="docker compose"
  else
    DOCKER_COMPOSE_BIN=""
  fi
}

check_env() {
  local missing=0
  if [ -z "${DISCORD_TOKEN:-}" ]; then
    warn "DISCORD_TOKEN が設定されていません"
    missing=1
  fi
  if [ -z "${LOG_CHANNEL_ID:-}" ]; then
    warn "LOG_CHANNEL_ID が設定されていません"
    missing=1
  fi
  if [ "$missing" -eq 1 ]; then
    err ".env を設定してください（DISCORD_TOKEN, LOG_CHANNEL_ID）"
  fi
  return 0
}

start_voicevox() {
  detect_compose
  if [ -z "$DOCKER_COMPOSE_BIN" ]; then
    warn "docker compose が見つからないため VoiceVox は起動しません（音声通知は失敗します）"
    return 0
  fi

  log "VoiceVox Engine を起動します..."
  UV_CACHE_DIR="$UV_CACHE_DIR" $DOCKER_COMPOSE_BIN -f "$PROJECT_ROOT/docker-compose.yml" up -d voicevox

  # 起動確認（30秒待機）
  local try=0
  while [ $try -lt 30 ]; do
    if curl -sf "${VOICEVOX_URL:-http://localhost:50021}/version" >/dev/null 2>&1; then
      log "VoiceVox Engine が起動しました"
      return 0
    fi
    sleep 1
    try=$((try + 1))
  done
  warn "VoiceVox の起動確認に失敗しました（音声通知は失敗します）"
}

stop_voicevox() {
  detect_compose
  [ -z "$DOCKER_COMPOSE_BIN" ] && return 0
  UV_CACHE_DIR="$UV_CACHE_DIR" $DOCKER_COMPOSE_BIN -f "$PROJECT_ROOT/docker-compose.yml" stop voicevox >/dev/null 2>&1 || true
}

start_processes() {
  check_env
  require_cmd uv
  command -v ffmpeg >/dev/null 2>&1 || warn "ffmpeg が見つかりません（音声再生に必要です）"
  start_voicevox

  if [ -f "$RUN_DIR/bot.pid" ] && kill -0 "$(cat "$RUN_DIR/bot.pid")" 2>/dev/null; then
    err "Bot Daemon が既に起動しています (pid=$(cat "$RUN_DIR/bot.pid"))"
  fi

  log "Discord Bot Daemon を起動します..."
  UV_CACHE_DIR="$UV_CACHE_DIR" uv run mcp-discord-bot-daemon >"$LOG_DIR/bot.log" 2>&1 &
  echo $! >"$RUN_DIR/bot.pid"

  log "起動完了: VoiceVox + Bot Daemon（MCPサーバーはこのスクリプトでは起動しません）"
  log "logs=$LOG_DIR, pids=$RUN_DIR"
}

stop_processes() {
  for name in bot; do
    local pidfile="$RUN_DIR/$name.pid"
    if [ -f "$pidfile" ]; then
      local pid
      pid=$(cat "$pidfile")
      if kill -0 "$pid" 2>/dev/null; then
        log "$name (pid=$pid) を停止します..."
        kill "$pid" || true
      else
        warn "$name の PID ファイルはありますがプロセスが見つかりません"
      fi
      rm -f "$pidfile"
    else
      warn "$name の PID ファイルがありません"
    fi
  done
  stop_voicevox
  log "停止完了"
}

case "${1:-start}" in
  start) start_processes ;;
  stop) stop_processes ;;
  *) err "使い方: $0 [start|stop]" ;;
esac
