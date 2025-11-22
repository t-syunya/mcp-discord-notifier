.PHONY: help format lint type-check check all

help:
	@echo "利用可能なコマンド:"
	@echo "  make format      - Ruff でコードをフォーマット"
	@echo "  make lint        - Ruff でリントチェック"
	@echo "  make type-check  - Ty で型チェック"
	@echo "  make check       - format, lint, type-check を順次実行"
	@echo "  make all         - check のエイリアス"

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
