# ポータブル一括起動提案（VoiceVox + Discord Bot + MCP）

## ゴール
- リポジトリをどのパスに置いても、同じコマンドで VoiceVox・Discord Bot・MCP サーバーをまとめて起動できる。
- 依存する Docker や `uv` の有無を自動で検出し、安全に起動・停止できる。
- PID やログの保存先をリポジトリ内に閉じ、他ユーザー環境と衝突しないようにする。

## 提案: `scripts/launch_all.sh` を追加する
`scripts/launch_all.sh` を追加しました。パスを気にせず一括起動できます。`make start-all` よりも「リポジトリローカルに閉じた PID/ログ管理」と「起動前チェック」を強化しています。

### 仕様
- **リポジトリルート自動解決**: `PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"` でスクリプト位置からルートを特定。
- **環境変数の自動読み込み**: `set -a; [ -f "$PROJECT_ROOT/.env" ] && source "$PROJECT_ROOT/.env"; set +a`。必要最低限のキー（`DISCORD_TOKEN`, `LOG_CHANNEL_ID`）が無ければ即エラー。
- **キャッシュ/実行ファイルパスを固定**: `UV_CACHE_DIR="$PROJECT_ROOT/.uv-cache"`、`RUN_DIR="$PROJECT_ROOT/.run"`、`LOG_DIR="$PROJECT_ROOT/.logs"`。他ユーザーや他インストールと競合しません。
- **VoiceVox 起動**: `docker compose -f "$PROJECT_ROOT/docker-compose.yml" up -d voicevox`（`docker-compose` / `docker compose` 自動判定）。起動確認を HTTP で 30 秒リトライ。
- **Bot + MCP をバックグラウンド起動**:
  - `uv run mcp-discord-bot-daemon > "$LOG_DIR/bot.log" 2>&1 & echo $! > "$RUN_DIR/bot.pid"`
  - `uv run mcp-discord-notifier --log-thread-name "${LOG_THREAD_NAME:-Conversation Log}" > "$LOG_DIR/mcp.log" 2>&1 & echo $! > "$RUN_DIR/mcp.pid"`
- **停止コマンド**: `scripts/launch_all.sh stop` で PID を読んで `kill`、VoiceVox を `docker compose stop voicevox`。PID が無ければスキップ。
- **前提確認**: `uv` / `docker` / `ffmpeg` の存在チェックと警告を冒頭で実行。

### 使い方
- 一括起動: `./scripts/launch_all.sh`（または `start` 明示）
- 停止: `./scripts/launch_all.sh stop`
- 任意のディレクトリから実行したい場合: `alias mcp-notifier="${PWD}/scripts/launch_all.sh"` をシェルに追加するだけで、クローン位置を気にせず起動可能。

## ログイン時の自動起動（任意）
ユーザーサービスとして起動したい場合、上記スクリプトを `ExecStart` に据えた systemd ユニットを作成します（パスのみ自身の環境に合わせるだけで動作）。

`~/.config/systemd/user/mcp-discord-notifier.service`
```ini
[Unit]
Description=MCP Discord Notifier (VoiceVox + Bot + MCP)
After=network.target docker.service

[Service]
Type=simple
WorkingDirectory=/path/to/mcp-discord-notifier
ExecStart=/path/to/mcp-discord-notifier/scripts/launch_all.sh start
ExecStop=/path/to/mcp-discord-notifier/scripts/launch_all.sh stop
Restart=on-failure

[Install]
WantedBy=default.target
```
有効化コマンド:
```bash
systemctl --user daemon-reload
systemctl --user enable --now mcp-discord-notifier.service
```
※ リポジトリを別パスへ移動したら `WorkingDirectory` と `ExecStart` のみ書き換えればよいです（その他は共通）。

## 実装手順の最小サマリ
1. `scripts/launch_all.sh` を利用する（実行権限済み）。  
2. `.run` と `.logs` を `.gitignore` に追加済み。  
3. 必要なら `make start-all` を `./scripts/launch_all.sh start` に置き換えるか、ラップする。  
4. 自動起動したい場合は systemd ユニットを作成し、`WorkingDirectory` のみ環境に合わせて設定。  

この構成なら、どのユーザー・どのディレクトリにクローンしても同じ操作で VoiceVox/Bot/MCP を起動できます。
