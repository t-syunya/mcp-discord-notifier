# テストガイド

MCP Discord Notifierのテストスイートです。

## テスト結果サマリー

```
✅ ユニットテスト:           32 passed (100%)
✅ 統合テスト (自動実行可能):  4 passed, 1 skipped
✅ 全テスト (手動除く):      36 passed, 1 skipped
⏸️ 手動テスト:              3 tests (手動実行が必要)
```

**全40テスト**
- 自動実行可能: 37テスト（36 passed, 1 skipped）
- 手動実行必要: 3テスト

## テストの種類

### 1. ユニットテスト
個々のモジュールの機能をテストします。

- `test_settings.py` - 設定管理のテスト
- `test_voicevox_client.py` - VoiceVoxクライアントのテスト
- `test_discord_logger.py` - Discordロガーのテスト
- `test_mcp_server.py` - MCPサーバーのテスト

### 2. 統合テスト
実際のDiscord接続を使用したテストです。

- `test_integration.py` - フルワークフローのテスト

### 3. 手動テスト
手動での確認が必要なテストです。

- `test_voice.py` - 音声機能の基本テスト
- `test_voice_persistent.py` - 永続的音声接続のテスト

## テストの実行

### すべてのユニットテストを実行（推奨）

```bash
uv run pytest test/ -m "not integration and not manual" -v
```

### 統合テストを含む全テスト実行（手動テスト除く）

```bash
uv run pytest test/ -m "not manual" -v
```

### 特定のテストファイルを実行

```bash
uv run pytest test/test_settings.py -v
```

### 特定のテストクラスを実行

```bash
uv run pytest test/test_settings.py::TestSettings -v
```

### 特定のテストメソッドを実行

```bash
uv run pytest test/test_settings.py::TestSettings::test_settings_from_env -v
```

### 統合テストのみ実行（Discord接続が必要）

```bash
# .envファイルが設定されていることを確認
uv run pytest test/ -m "integration and not manual" -v
```

### 手動テストを実行

```bash
# wait_for_reactionの手動テスト
uv run pytest test/test_integration.py::TestManualInteraction::test_wait_for_reaction_manual -v

# 音声通知の手動テスト
uv run pytest test/test_integration.py::TestManualInteraction::test_voice_notification_manual -v

# 永続的音声接続テスト
uv run pytest test/test_voice_persistent.py -v
```

### カバレッジレポート付きで実行

```bash
# カバレッジ測定ツールをインストール
uv add --dev pytest-cov

# カバレッジ付きで実行
pytest test/ --cov=src --cov-report=html
```

## テストマーカー

テストには以下のマーカーが付いています：

- `integration` - 統合テスト（実際のDiscord接続が必要）
- `manual` - 手動テスト（人間の介入が必要）

### マーカーでフィルタリング

```bash
# 統合テストのみ実行
pytest -m integration

# 統合テストを除外
pytest -m "not integration"

# 手動テストのみ実行
pytest -m manual
```

## pytest設定

プロジェクトルートに`pytest.ini`を作成して設定をカスタマイズできます：

```ini
[pytest]
testpaths = test
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    integration: Integration tests requiring Discord connection
    manual: Manual tests requiring human interaction
asyncio_mode = auto
```

## モック（Mock）について

ユニットテストでは、外部依存（Discord API、VoiceVox API等）をモックしています。

**例：**
```python
from unittest.mock import AsyncMock, MagicMock, patch

# Discord clientをモック
mock_client = MagicMock()
mock_client.is_ready.return_value = True

# 非同期メソッドをモック
mock_client.wait_for = AsyncMock(return_value=("reaction", "user"))
```

## テストデータ

テストで使用するダミーデータ：

- Discord Token: `test-token-123`
- Channel ID: `123456789012345678`
- Voice Channel ID: `987654321098765432`
- Thread Name: `Test Thread`

## トラブルシューティング

### `ImportError: cannot import name 'X' from 'src'`

```bash
# プロジェクトルートから実行していることを確認
cd /path/to/mcp-discord-notifier
pytest test/
```

### `ModuleNotFoundError: No module named 'pytest'`

```bash
# 依存関係を再インストール
uv sync
```

### 統合テストが失敗する

1. `.env`ファイルが正しく設定されているか確認
2. Discordボットが起動しているか確認
3. ボットに必要な権限があるか確認

```bash
# .envファイルの確認
cat .env

# 手動でサーバーを起動してテスト
./scripts/start.sh
```

### 非同期テストでエラーが出る

```bash
# pytest-asyncioが正しくインストールされているか確認
uv list | grep pytest-asyncio

# 再インストール
uv add --dev pytest-asyncio
```

## CI/CDでのテスト実行

GitHub Actionsの例：

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Install uv
        run: pip install uv
      - name: Install dependencies
        run: uv sync
      - name: Run unit tests
        run: uv run pytest test/ -m "not integration and not manual" -v --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

**注意**: CI/CDでは統合テスト（`integration`マーカー）と手動テスト（`manual`マーカー）を除外します。これらのテストは実際のDiscord接続や人間の操作が必要なためです。

## 新しいテストの追加

新しいテストを追加する場合：

1. `test/`ディレクトリに`test_*.py`ファイルを作成
2. テストクラスは`Test*`で始める
3. テストメソッドは`test_*`で始める
4. 非同期テストには`@pytest.mark.asyncio`を付ける

**例：**
```python
import pytest

class TestNewFeature:
    """Test suite for new feature."""

    @pytest.mark.asyncio
    async def test_something(self):
        """Test something."""
        result = await some_async_function()
        assert result == expected
```

## 参考リンク

- [pytest公式ドキュメント](https://docs.pytest.org/)
- [pytest-asyncio](https://github.com/pytest-dev/pytest-asyncio)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
