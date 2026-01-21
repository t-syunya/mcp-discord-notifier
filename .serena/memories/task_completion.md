# タスク完了時に実施
- 差分確認: `git status`, `git diff`
- チェック実行: `uv run pytest -q`、`uv run --group dev ruff check src test`、必要なら `uv run --group dev ruff format`、`PYTHONPATH=src uv run --group dev ty check src/`
- 起動確認が必要なら `uv run mcp-discord-notifier` もしくは `make mcp` で手動動作確認。
- コミット方針(AGENTS): 既存変更を巻き戻さず、メッセージは `prefix: 日本語概要` 形式で作成。秘密情報(.envなど)をコミットしない。
- 共有時は環境変数値を出さない。VoiceVox未起動環境では音声連携が失敗する点を確認。