# プロジェクト概要
- 目的: AI開発アシスタント(Claude Code/Cursor/Codex等)がDiscord経由でユーザーへ通知・音声連携するMCPサーバー兼Discord Bot。リアルタイムログ送信、リアクション待機、VoiceVox音声通知を提供。
- 技術スタック: Python 3.12, discord.py[voice], mcp[cli], FastAPI/uvicorn, httpx, Pydantic(+settings), PyNaCl。ビルドは hatchling。
- エントリポイント: `mcp-discord-notifier` (MCPサーバー), `mcp-discord-bot-daemon` (Discord+VoiceVox常駐) が `src/__main__.py` と `src/bot_daemon.py` で定義。
- 主構成: `src/mcp_server.py` (MCPエンドポイント), `src/discord_logger.py` (Discord埋め込み生成), `src/voicevox_client.py` (VoiceVox連携), `src/settings.py` (設定), `src/command_handler.py`/`bot_daemon.py` (Discordコマンド/デーモン)。`test/` にユニット・統合テスト。`scripts/start.sh`, `docker-compose.yml` でVoiceVox起動。
- 環境変数: `.env.example` をコピーし、最低 `DISCORD_TOKEN`, `LOG_CHANNEL_ID` 必須。VoiceVox利用時に `VOICEVOX_URL`, `VOICE_CHANNEL_ID`, `VOICE_SPEAKER_ID` など。
- 既知の運用ガイド: MCPクライアント登録は `uv run mcp-discord-notifier` を bash で起動し、`UV_CACHE_DIR` をリポジトリ配下に指定して権限問題回避。