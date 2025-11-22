# Repository Guidelines

## MCP利用状況と確認手順
- 2025-11-22時点で、Claude Code から本MCPが正常に利用できることを確認済み（ユーザー報告）。
- 2025-11-22時点で、Codex CLI から本MCPを登録済み（`codex mcp list` で `enabled` を確認済み）。起動コマンドは `uv run mcp-discord-notifier --log-thread-name "Conversation Log"` を bash 経由で実行し、`UV_CACHE_DIR=/home/kkts0/Projects/mcp-discord-notifier/.uv-cache` を指定して権限問題を回避しています。
- ローカル環境で利用可否を確認する場合は以下を実行してください：
  1. `claude mcp list | grep mcp-discord-notifier` で登録状態を確認
  2. 未登録の場合は `claude mcp add mcp-discord-notifier -- bash -c "cd /mnt/l/WSL/Projects/mcp-discord-notifier && uv run mcp-discord-notifier"`
  3. 必要に応じて `.env` に `DISCORD_TOKEN` と `LOG_CHANNEL_ID` を設定し、`uv run mcp-discord-notifier --log-thread-name "Conversation Log"` で起動確認
  4. Codexで確認する場合は `codex mcp list` を実行し、`mcp-discord-notifier` が `enabled` 状態で表示されることを確認。未登録なら下記で追加（ローカルキャッシュ先を明示）：
     `codex mcp add mcp-discord-notifier --env DISCORD_TOKEN="$DISCORD_TOKEN" --env LOG_CHANNEL_ID="$LOG_CHANNEL_ID" --env LOG_THREAD_NAME="${LOG_THREAD_NAME:-Conversation Log}" --env UV_CACHE_DIR="/home/kkts0/Projects/mcp-discord-notifier/.uv-cache" -- bash -c "cd /home/kkts0/Projects/mcp-discord-notifier && uv run mcp-discord-notifier --log-thread-name \"${LOG_THREAD_NAME:-Conversation Log}\""`

## プロジェクト構成とモジュール概要
- `src/` にはエージェント本体があり、`mcp_server.py` がMCPエンドポイント、`discord_logger.py` がDiscord埋め込み生成、`voicevox_client.py` がVoiceVox連携を担います。設定値は `settings.py` に集約されています。
- `test/` ではユニット・統合テストを整理しており、`test_voice_persistent.py` は音声キャッシュ、`test_integration.py` はDiscordモックを用いたエンドツーエンド検証です。
- ルート直下の `docker-compose.yml` と `scripts/start.sh` はVoiceVoxエンジン付き起動の定石です。環境変数は `.env`（`.env.example` をコピー）に保存してください。

## ビルド・テスト・開発コマンド
```bash
uv sync                      # 依存関係をインストール
uv run mcp-discord-notifier  # MCPサーバーをローカル起動
uv run pytest -q             # 全テストを実行
uv run ruff check src test   # コードスタイル検証
./scripts/start.sh           # VoiceVoxとサーバーを一括起動
```
各コマンドは最低限の前提として Python 3.12 と `uv` が利用可能であることを想定しています。

## コーディングスタイルと命名規則
- Python 3.12 を前提にし、`ruff` でPEP 8準拠、`pyproject.toml` 設定を尊重します。
- 関数・変数は `snake_case`、クラスは `PascalCase`、定数は `UPPER_SNAKE_CASE` を使用してください。
- 非公開属性には接頭辞 `_` を付与し、Discordイベント名やMCPツールIDは文字列リテラルで統一します。

## テスト指針
- テストは `pytest` と `pytest-asyncio` を用いています。新規テストは `test_*.py` に追加し、協調的な非同期テストでは `asyncio` フィクスチャを再利用してください。
- 重要なワークフローにはモックレス統合テストを追加し、最低限 happy / failure パスを両方網羅します。
- 音声関連は VoiceVox が無い環境でも通るよう、HTTPモックと一時ディレクトリを併用してください。

## コミットおよびPRガイドライン
- 現在の履歴は初期化段階のため、`feat: ...` や `fix: ...` 形式のConventional Commitsを推奨します。短く具体的な概要と、本文で動機・副作用を記述してください。
- PRでは目的、主要変更点、テスト結果（`uv run pytest -q`）を箇条書きで記入し、関連Issueやログスクリーンショットを添えてください。
- 秘密情報はコミットに含めず、`.env` と `settings.py` の差分はローカル検証に留めることを確認してください。

## セキュリティと設定のヒント
- `.env` には `DISCORD_TOKEN`、`LOG_CHANNEL_ID`、必要に応じて `VOICEVOX_URL` と `VOICE_SPEAKER_ID` を設定します。共有時は `env` ではなくサンプルやドキュメントで値を伝達してください。
- Docker利用時は `docker-compose logs voicevox` でエラーチェックし、公開インターフェースを必要最小限に絞ります。
- Discord権限は送信とスレッド作成を必須とし、音声権限は音声通知を有効化する場合のみ付与してください。
