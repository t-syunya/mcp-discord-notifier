# MCP Discord Notifier - クライアント設定ガイド

このドキュメントは、AI開発アシスタント（Claude Code、Cursor、Codex等）でMCP Discord Notifierを使用するための設定方法を説明します。

## 前提条件

- MCP Discord Notifierサーバーがインストール済みであること
- `.env`ファイルが設定済みであること
- `uv`または`pip`で依存関係がインストール済みであること

## Claude Code

### グローバル設定（全プロジェクトで使用）

**方法1: インストール済みコマンドを使用（推奨）**

```bash
# uv でインストール済みの場合
claude mcp add -s user mcp-discord-notifier mcp-discord-notifier
```

**方法2: uvを経由して実行**

```bash
# プロジェクトディレクトリ内で uv run を使用
claude mcp add -s user mcp-discord-notifier \
  -- bash -c "cd /path/to/mcp-discord-notifier && uv run mcp-discord-notifier"
```

### プロジェクトローカル設定

```bash
cd /path/to/your/project
claude mcp add mcp-discord-notifier mcp-discord-notifier
```

### 環境変数を直接指定する場合

```bash
claude mcp add -s user mcp-discord-notifier mcp-discord-notifier \
  -e DISCORD_TOKEN="your-bot-token" \
  -e LOG_CHANNEL_ID="123456789012345678" \
  -e LOG_THREAD_NAME="AI Conversation" \
  -e VOICE_CHANNEL_ID="123456789012345678" \
  -e VOICEVOX_URL="http://localhost:50021"
```

**注意**: 環境変数を指定しない場合、`.env` ファイルから自動的に読み込まれます。

---

## Cursor

### 設定ファイルの場所

`~/.cursor/mcp.json` または `~/.config/cursor/mcp.json`

### .envファイルを使用する方法（推奨）

```json
{
  "mcpServers": {
    "mcp-discord-notifier": {
      "command": "bash",
      "args": [
        "-c",
        "cd /path/to/mcp-discord-notifier && uv run mcp-discord-notifier"
      ]
    }
  }
}
```

### 環境変数を直接指定する方法

```json
{
  "mcpServers": {
    "mcp-discord-notifier": {
      "command": "mcp-discord-notifier",
      "args": [],
      "env": {
        "DISCORD_TOKEN": "your-bot-token",
        "LOG_CHANNEL_ID": "123456789012345678",
        "LOG_THREAD_NAME": "AI Conversation",
        "VOICE_CHANNEL_ID": "123456789012345678",
        "VOICEVOX_URL": "http://localhost:50021"
      }
    }
  }
}
```

### Python仮想環境を使用する場合

```json
{
  "mcpServers": {
    "mcp-discord-notifier": {
      "command": "/path/to/mcp-discord-notifier/.venv/bin/python",
      "args": ["-m", "src"],
      "cwd": "/path/to/mcp-discord-notifier"
    }
  }
}
```

---

## Codex

### CLIで設定（推奨）

```bash
# プロジェクトディレクトリに移動
cd /path/to/mcp-discord-notifier

# MCPサーバーを追加
codex mcp add mcp-discord-notifier \
  -- bash -c "cd /path/to/mcp-discord-notifier && uv run mcp-discord-notifier"
```

### 環境変数を指定する場合

```bash
codex mcp add mcp-discord-notifier \
  --env DISCORD_TOKEN="your-bot-token" \
  --env LOG_CHANNEL_ID="123456789012345678" \
  --env LOG_THREAD_NAME="AI Conversation" \
  --env VOICE_CHANNEL_ID="123456789012345678" \
  --env VOICEVOX_URL="http://localhost:50021" \
  -- mcp-discord-notifier
```

### config.tomlで直接編集

`~/.codex/config.toml` を編集：

```toml
[mcp_servers.mcp-discord-notifier]
command = "bash"
args = [
  "-c",
  "cd /path/to/mcp-discord-notifier && uv run mcp-discord-notifier"
]

# 環境変数を指定する場合（オプション）
[mcp_servers.mcp-discord-notifier.env]
DISCORD_TOKEN = "your-bot-token"
LOG_CHANNEL_ID = "123456789012345678"
LOG_THREAD_NAME = "AI Conversation"
VOICE_CHANNEL_ID = "123456789012345678"
VOICEVOX_URL = "http://localhost:50021"
```

### 設定の確認

```bash
# MCPサーバー一覧を表示
codex mcp list

# Codex CLIで動作確認
codex
# チャット内で /mcp と入力
```

---

## その他のMCPクライアント

### 基本的な設定形式

ほとんどのMCPクライアントは以下の形式をサポートしています：

```json
{
  "mcpServers": {
    "mcp-discord-notifier": {
      "command": "実行コマンド",
      "args": ["引数1", "引数2"],
      "env": {
        "環境変数名": "値"
      }
    }
  }
}
```

---

## 利用可能なツール

MCPサーバーが提供する3つのツール：

### 1. log_conversation

会話をDiscordに記録します。

```json
{
  "role": "assistant",
  "message": "タスクが完了しました",
  "context": "feature/new-feature"
}
```

### 2. wait_for_reaction

ユーザーからのリアクション（絵文字）を待機します。

```json
{
  "message": "このまま続けますか？",
  "options": ["✅ 続行", "❌ 中止"],
  "timeout": 300
}
```

### 3. notify_voice

音声通知を送信します（ボイスチャンネルへの接続が必要）。

```json
{
  "voice_channel_id": 123456789012345678,
  "message": "ビルドが完了しました",
  "priority": "high",
  "speaker_id": 1
}
```

---

## 音声通知の使い方

### 1. .envファイルで自動接続（推奨）

`.env`ファイルに以下を追加：
```bash
VOICE_CHANNEL_ID=123456789012345678
```

サーバーが起動すると自動的にボイスチャンネルに接続されます。

### 2. Discordコマンドで手動接続

Discordのログチャンネルで以下のコマンドを入力：

**デフォルトチャンネルに接続（.envで設定済みの場合）:**
```
!join
```

**特定のチャンネルに接続:**
```
!join 123456789012345678
```

**切断:**
```
!leave
```

### 3. AIアシスタントから音声通知を送信

接続後、AIアシスタントに自然言語で依頼します。AIが状況に応じて自動的に適切なツールを選択します。

**例：**
- 「ビルドが完了したら音声で通知して」
- 「この作業が終わったら声で教えて」
- 「テストが通ったらボイスチャンネルで報告して」
- 「エラーが発生したら音声で警告して」

AIアシスタントは文脈を理解し、`notify_voice`ツールを自動的に使用して音声通知を送信します。

---

## トラブルシューティング

### MCPサーバーが起動しない

1. **コマンドパスを確認**
   ```bash
   which mcp-discord-notifier
   ```

2. **手動で起動してエラーを確認**
   ```bash
   cd /path/to/mcp-discord-notifier
   uv run mcp-discord-notifier
   ```

3. **環境変数を確認**
   ```bash
   cat .env
   ```

### ツールが表示されない

- MCPクライアントを再起動
- 設定ファイルのJSON/TOML構文を確認
- MCPサーバーのログを確認

### 音声通知が機能しない

1. **ボイスチャンネルに接続されているか確認**
   - Discordで`!join`コマンドを実行

2. **VoiceVoxが起動しているか確認**
   ```bash
   curl http://localhost:50021/version
   ```

3. **ボットに必要な権限があるか確認**
   - Connect（接続）
   - Speak（発言）

---

## 使用例

### 基本的な使い方

AIアシスタントとの会話で、自然に依頼するだけでMCPツールが自動的に使用されます。

**例1: 作業の記録**
```
ユーザー: 「認証機能の実装を開始します」
AI: 「承知しました。Discordに記録します」
→ AIが自動的にlog_conversationツールを使用
```

**例2: ユーザー確認が必要な場合**
```
ユーザー: 「データベースをリセットして良いか確認して」
AI: 「Discordで確認メッセージを送信します」
→ AIが自動的にwait_for_reactionツールを使用
→ ユーザーがDiscordでリアクション
AI: 「承認されました。データベースをリセットします」
```

**例3: 長時間タスクの完了通知**
```
ユーザー: 「ビルドとテストが終わったら声で教えて」
AI: 「承知しました」
→ タスク完了後、AIが自動的にnotify_voiceツールを使用
→ ボイスチャンネルで音声通知
```

### ポイント

- **ツール名を明示する必要はありません** - AIが自動的に適切なツールを選択
- **自然な言葉で依頼できます** - 「記録して」「確認して」「通知して」など
- **文脈を理解します** - タスクの性質に応じて最適なツールを使用

---

## サポート

問題が発生した場合は、[GitHub Issues](https://github.com/your-username/mcp-discord-notifier/issues)で報告してください。
