# コードスタイル/規約
- Python 3.12前提。PEP8準拠、`ruff` によるフォーマット+lint (`pyproject.toml` 設定)。型チェックは `ty`。
- 命名: 関数/変数 snake_case、クラス PascalCase、定数 UPPER_SNAKE_CASE。非公開属性は `_` 接頭辞。Discordイベント名やMCPツールIDは文字列リテラル統一。
- Docstring/型: Pydantic v2 ベース。型ヒント推奨。
- コメント: 必要最小限。VoiceVox/Discord連携は明示的に扱う。
- Git運用(AGENTS): コミットメッセージは `prefix: 日本語概要` 形式。既存変更を勝手に巻き戻さない。