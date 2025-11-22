# MCP Discord Notifier

AI開発アシスタント（Claude Code、Cursor、Codex等）がDiscordを通じてユーザーとインタラクティブにコミュニケーションできるMCP（Model Context Protocol）サーバーです。リアルタイム通知、ユーザーフィードバック、音声通知機能を提供します。

## 目次

- [クイックスタート](#クイックスタート)
- [概要](#概要)
- [機能](#機能)
- [必要要件](#必要要件)
- [インストール](#インストール)
- [セットアップ](#セットアップ)
  - [1. Discordボットの作成](#1-discordボットの作成)
  - [2. VoiceVoxのセットアップ（オプション）](#2-voicevoxのセットアップオプション)
  - [3. FFmpegのインストール](#3-ffmpegのインストール)
- [設定](#設定)
  - [環境変数](#環境変数)
  - [Claude Code](#claude-code)
  - [Cursor / その他のMCPクライアント](#cursor--その他のmcpクライアント)
- [使い方](#使い方)
  - [利用可能なツール](#利用可能なツール)
  - [実行例](#実行例)
- [Discordボットコマンド](#discordボットコマンド)
- [VoiceVox統合](#voicevox統合)
- [トラブルシューティング](#トラブルシューティング)
- [開発](#開発)
- [ライセンス](#ライセンス)

## クイックスタート

5分で始める最短手順：

### 1. インストール
```bash
git clone https://github.com/your-username/mcp-discord-notifier.git
cd mcp-discord-notifier
uv sync
```

### 2. Discord設定
1. [Discord Developer Portal](https://discord.com/developers/applications) でボットを作成
2. ボットトークンをコピー
3. ボットをサーバーに招待（権限: Send Messages, Create Threads, Message Content Intent）
4. チャンネルIDを取得（右クリック → IDをコピー）

### 3. 環境設定
```bash
cp .env.example .env
nano .env  # DISCORD_TOKENとLOG_CHANNEL_IDを設定
```

### 4. MCPクライアントに登録

**Claude Code:**
```bash
claude mcp add mcp-discord-notifier \
  -- bash -c "cd $(pwd) && uv run mcp-discord-notifier"
```

**Cursor:**
`~/.cursor/mcp.json`に追加：
```json
{
  "mcpServers": {
    "mcp-discord-notifier": {
      "command": "bash",
      "args": ["-c", "cd /path/to/mcp-discord-notifier && uv run mcp-discord-notifier"]
    }
  }
}
```

### 5. サーバーを起動

**方法A: MCPクライアント経由（個人利用）**
```bash
# Claude Codeを起動するだけ
# MCPクライアントが自動的にサーバーを起動します
```

**方法B: 手動起動（常時稼働）**
```bash
# サーバーを起動
./scripts/start.sh

# バックグラウンドで起動
nohup ./scripts/start.sh > /dev/null 2>&1 &
```

### 6. 使ってみる

**AIアシスタントで:**
```
ユーザー: 「Discordに進捗を報告して」
AI: ✅ [自動的にlog_conversationツールを実行]
```

**Discordで:**
```
!help    # コマンド一覧
!status  # ボットの状態確認
```

**完了！** 詳細は以下のセクションを参照してください。

---

## 概要

このMCPサーバーは、AI開発ツールとDiscordを橋渡しし、以下を可能にします：

- **リアルタイム通知**: AIエージェントが進捗状況や質問をDiscordに送信
- **インタラクティブフィードバック**: Discordのリアクションでワークフローを制御
- **音声通知**: VoiceVoxを使った日本語音声による通知
- **監査証跡**: タイムスタンプとコンテキスト付きの完全な会話履歴

### 利用シーン

- **長時間タスク**: AIが集中的な処理を完了したときに通知を受け取る
- **意思決定ポイント**: 重要な変更前にAIがユーザー確認を求める
- **バックグラウンド開発**: 他の作業をしながらAIの進捗状況を監視
- **チーム協働**: AI対話履歴をチームメンバーと共有
- **音声通知**: ボイスチャンネルで重要なイベントを音声でアナウンス

## 機能

### ✅ 実装済み機能

- **メッセージロギング** (`log_conversation`)
  - 異なるロール（human、assistant、system）でメッセージをログ
  - 色分けされたDiscord埋め込みメッセージ
  - 自動スレッド作成と管理
  - タイムスタンプとコンテキスト情報

- **リアクション待機** (`wait_for_reaction`)
  - ユーザーからのリアクション（絵文字）を待機
  - 複数選択肢のサポート
  - タイムアウト設定可能
  - ユーザー承認・拒否・選択のワークフロー

- **音声通知** (`notify_voice`)
  - VoiceVoxによる日本語TTS
  - ボイスチャンネルでの音声再生
  - 複数のスピーカー（声質）選択
  - 優先度設定（normal/high）
  - VoiceVox未利用時の自動フォールバック

### 🚧 計画中の機能

- スマート通知ルール（イベントタイプ別）
- ボイスチャンネルでの双方向コミュニケーション
- より多くのTTSエンジンのサポート

## 必要要件

### 必須
- Python 3.12以上
- Discordアカウントとボット
- MCP対応のAIクライアント（Claude Code、Cursor、Codex等）

### オプション（音声通知機能を使用する場合）
- Docker & Docker Compose
- FFmpeg

## インストール

```bash
# リポジトリをクローン
git clone https://github.com/your-username/mcp-discord-notifier.git
cd mcp-discord-notifier

# 依存関係をインストール
uv sync

# または pip を使用
pip install -e .
```

## セットアップ

### 1. Discordボットの作成

1. **Discord Developer Portalにアクセス**
   - https://discord.com/developers/applications

2. **新しいアプリケーションを作成**
   - "New Application"ボタンをクリック
   - アプリケーション名を入力

3. **ボットを作成**
   - 左サイドバーの"Bot"セクションに移動
   - "Add Bot"をクリック
   - ボットトークンをコピー（後で使用）

4. **権限を設定**

   Bot → Bot Permissions で以下を有効化:
   - ✅ Send Messages
   - ✅ Create Public Threads
   - ✅ Read Message History
   - ✅ Embed Links
   - ✅ Connect（音声通知を使用する場合）
   - ✅ Speak（音声通知を使用する場合）

5. **特権インテントを有効化**

   Bot → Privileged Gateway Intents で:
   - ✅ Message Content Intent

6. **ボットをサーバーに招待**

   OAuth2 → URL Generator で:
   - Scopes: `bot`
   - Bot Permissions: 上記で設定した権限
   - 生成されたURLでボットを招待

7. **チャンネルIDを取得**
   - Discordで開発者モードを有効化（設定 → 詳細設定 → 開発者モード）
   - ログを記録したいチャンネルを右クリック → "IDをコピー"

### 2. VoiceVoxのセットアップ（オプション）

音声通知機能を使用する場合、VoiceVox Engineをセットアップします。

```bash
# VoiceVox Engineを起動（Dockerを使用）
docker-compose up -d

# 起動確認
curl http://localhost:50021/version
```

**成功すると**、バージョン情報のJSONが返されます。

**VoiceVoxなしで使用する場合**: `notify_voice`ツールは自動的にテキストログのみにフォールバックします。

#### 利用可能なスピーカー

```bash
# スピーカー一覧を取得
curl http://localhost:50021/speakers | jq
```

**主要なスピーカーID:**
- `1`: 四国めたん（ノーマル）
- `3`: ずんだもん（ノーマル）
- `8`: 春日部つむぎ（ノーマル）
- `10`: 雨晴はう（ノーマル）
- `11`: 波音リツ（ノーマル）

### 3. FFmpegのインストール

音声再生にはFFmpegが必要です。

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# macOS (Homebrew)
brew install ffmpeg

# Windows
# https://ffmpeg.org/download.html からダウンロードしてインストール
```

## 設定

### 環境変数の設定（.envファイル）

プロジェクトルートに`.env`ファイルを作成して設定を管理します：

```bash
# .env.exampleをコピーして.envを作成
cp .env.example .env

# .envファイルを編集
nano .env  # または好きなエディタで編集
```

**設定項目：**

| 変数名 | 説明 | デフォルト | 必須 |
|--------|------|-----------|------|
| `DISCORD_TOKEN` | Discordボットトークン | - | ✅ |
| `LOG_CHANNEL_ID` | ログ記録先のチャンネルID | - | ✅ |
| `LOG_THREAD_NAME` | スレッド名 | "Conversation Log" | ❌ |
| `VOICE_CHANNEL_ID` | デフォルトのボイスチャンネルID（自動接続用） | - | ❌ |
| `VOICEVOX_URL` | VoiceVox Engine URL | "http://localhost:50021" | ❌ |

**.env ファイルの例：**

```bash
DISCORD_TOKEN=your-discord-bot-token-here
LOG_CHANNEL_ID=123456789012345678
LOG_THREAD_NAME=Conversation Log
VOICEVOX_URL=http://localhost:50021
```

### Claude Code

#### グローバルインストール（すべてのプロジェクトで使用）

```bash
# .envファイルが配置されているディレクトリでサーバーを起動
claude mcp add -s user mcp-discord-notifier \
  /path/to/mcp-discord-notifier/run.sh
```

**run.sh の作成例：**

```bash
#!/bin/bash
cd "$(dirname "$0")"
uv run mcp-discord-notifier
```

または、環境変数を直接指定する場合：

```bash
claude mcp add -s user mcp-discord-notifier mcp-discord-notifier \
  -e DISCORD_TOKEN="your-discord-bot-token" \
  -e LOG_CHANNEL_ID="your-channel-id" \
  -e LOG_THREAD_NAME="AI Conversation" \
  -e VOICEVOX_URL="http://localhost:50021"
```

#### プロジェクトローカルインストール

```bash
# プロジェクトに.envファイルを配置して起動
cd /path/to/mcp-discord-notifier
cp .env.example .env
# .envを編集

claude mcp add mcp-discord-notifier ./run.sh
```

### Cursor / その他のMCPクライアント

MCP設定ファイル（`~/.cursor/mcp.json`または`~/.claude.json`）に以下を追加：

**.envファイルを使用する場合（推奨）：**

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

**環境変数を直接指定する場合：**

```json
{
  "mcpServers": {
    "mcp-discord-notifier": {
      "command": "mcp-discord-notifier",
      "args": [],
      "env": {
        "DISCORD_TOKEN": "your-discord-bot-token",
        "LOG_CHANNEL_ID": "123456789012345678",
        "LOG_THREAD_NAME": "AI Conversation",
        "VOICEVOX_URL": "http://localhost:50021"
      }
    }
  }
}
```

## 使い方

### 重要：新しいアーキテクチャ

**v0.2.0から、Discord BotとMCPサーバーが分離されました。**

#### アーキテクチャ概要

```
┌─────────────────────────────────┐
│  Discord Bot Daemon (常駐)       │
│  ポート: 8765                    │
│  - Discord接続維持               │
│  - !help等のコマンド処理          │
│  - ボイスチャンネル接続維持       │
│  - HTTP API                     │
└─────────────────────────────────┘
         ↑ HTTP通信
┌─────────────────────────────────┐
│  MCP Server (必要時起動)         │
│  - Claude Codeが自動起動         │
│  - log_conversation             │
│  - wait_for_reaction            │
│  - notify_voice                 │
└─────────────────────────────────┘
```

#### なぜ分離？

1. **Discord Bot Daemon（常駐必要）**
   - Discordコマンド（`!help`, `!join`等）の処理
   - ボイスチャンネル接続の維持
   - HTTP APIでリクエストを待ち受け

2. **MCP Server（必要時起動）**
   - Claude Codeが使用時のみ起動
   - HTTP経由でBot Daemonと通信
   - 軽量・高速に起動/終了可能

#### 2つの起動方法

##### 方法1: 自動起動（推奨）

MCPクライアントに登録すると、クライアントが自動的にサーバーを起動・維持します：

**Claude Code:**
```bash
claude mcp add mcp-discord-notifier \
  -- bash -c "cd $(pwd) && uv run mcp-discord-notifier"
```

**Cursor:**
`~/.cursor/mcp.json`に設定を追加すると、Cursor起動時にサーバーも起動します。

**メリット:**
- ✅ MCPクライアント起動時に自動起動
- ✅ 設定ファイルで管理
- ✅ MCPクライアント終了時に自動停止

**注意:**
- Discord Botコマンド（`!help`等）を使いたい場合は、MCPクライアントを起動しておく必要があります

##### 方法2: 手動起動（Botコマンドを常時使いたい場合）

Discord Botのコマンド機能を常時使いたい場合は、手動で起動します：

```bash
# 起動
./scripts/start.sh

# バックグラウンド起動（推奨）
nohup ./scripts/start.sh > /dev/null 2>&1 &

# 停止
./scripts/stop.sh
```

**メリット:**
- ✅ MCPクライアント起動前でもBotコマンドが使える
- ✅ 複数のMCPクライアントから同時に使用可能
- ✅ サーバーとして常時稼働

**systemdでサービス化する場合:**
```ini
# /etc/systemd/system/mcp-discord-notifier.service
[Unit]
Description=MCP Discord Notifier
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/mcp-discord-notifier
ExecStart=/path/to/mcp-discord-notifier/scripts/start.sh
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

#### 使用フロー

1. **.envファイルを設定** (初回のみ)
   ```bash
   cp .env.example .env
   nano .env  # DISCORD_TOKENとLOG_CHANNEL_IDを設定
   ```

2. **サーバーを起動**
   - 自動起動: MCPクライアントに登録
   - 手動起動: `./scripts/start.sh`

3. **使ってみる**
   - AIアシスタントに指示: 「Discordに進捗を報告して」
   - Discordでコマンド実行: `!help`, `!status`

---

### 利用可能なツール

#### 1. `log_conversation` - メッセージロギング

Discordにメッセージを記録します。

**パラメータ:**
```json
{
  "role": "human | assistant | system",
  "message": "ログするメッセージ内容",
  "context": "オプションのコンテキスト情報"
}
```

**使用例:**
```json
{
  "role": "assistant",
  "message": "認証機能の実装が完了しました",
  "context": "feature/auth-system"
}
```

**色分け:**
- **human**: 青 💬
- **assistant**: 緑 💬
- **system**: グレー 💬

#### 2. `wait_for_reaction` - ユーザー承認待機

メッセージを送信し、ユーザーのリアクションを待機します。

**パラメータ:**
```json
{
  "message": "確認を求めるメッセージ",
  "options": ["✅ 承認", "❌ 拒否", "⏸️ 一時停止"],
  "timeout": 300,
  "context": "オプションのコンテキスト"
}
```

**使用例:**
```json
{
  "message": "データベースのマイグレーションを実行しますか？",
  "options": ["✅ 実行する", "❌ キャンセル"],
  "timeout": 60
}
```

**戻り値:**
```json
{
  "emoji": "✅",
  "option": "✅ 実行する",
  "user": "username#1234",
  "message_id": 123456789
}
```

#### 3. `notify_voice` - 音声通知

ボイスチャンネルで音声通知を行います。

**パラメータ:**
```json
{
  "voice_channel_id": 123456789,
  "message": "読み上げるメッセージ",
  "priority": "normal | high",
  "speaker_id": 1
}
```

**使用例:**
```json
{
  "voice_channel_id": 987654321,
  "message": "デプロイが完了しました",
  "priority": "high",
  "speaker_id": 3
}
```

### 実行例

#### AIアシスタントでの使用

サーバーが起動していれば、AIアシスタントに自然言語で指示するだけです：

```
ユーザー: 「このタスクが完了したらDiscordに報告して」
AI: ✅ [log_conversation ツールを自動実行]

ユーザー: 「重要な変更前に確認を求めて」
AI: 🤔 [wait_for_reaction ツールを実行して、Discordでの応答を待機]

ユーザー: 「ビルドが終わったら音声で知らせて」
AI: 🔊 [notify_voice ツールを実行して、ボイスチャンネルで通知]
```

#### Discord Botコマンドの使用

サーバーが起動していれば、Discordのログチャンネルで直接コマンドを実行できます：

```
!help              # コマンド一覧を表示
!status            # ボットの状態を確認
!join              # ボイスチャンネルに接続
!say テスト完了     # 音声で通知
!speakers          # 利用可能なスピーカー一覧
```

詳細は [docs/COMMANDS.md](docs/COMMANDS.md) を参照してください。

## Discordボットコマンド

ログチャンネルでボットに対してコマンドを実行できます。すべてのコマンドは `!` で始まります。

### 主なコマンド

| コマンド | 説明 | エイリアス |
|---------|------|-----------|
| `!help [command]` | コマンド一覧または詳細ヘルプ | `!h`, `!?` |
| `!ping` | ボットのレイテンシーを確認 | - |
| `!status` | ボットの状態を表示 | `!info` |
| `!thread [name]` | 新しいログスレッドを作成 | - |
| `!join [channel_id]` | ボイスチャンネルに接続 | - |
| `!leave` | ボイスチャンネルから切断 | `!disconnect` |
| `!say <message>` | 音声でメッセージを読み上げ | `!speak`, `!tts` |
| `!speakers` | VoiceVoxスピーカー一覧 | - |

**使用例：**
```
!help              # 全コマンド表示
!status            # ボット状態確認
!join              # ボイスチャンネルに接続
!say テスト完了     # 音声で通知
```

詳細は [docs/COMMANDS.md](docs/COMMANDS.md) を参照してください。

### カスタムコマンドの追加

プログラムからカスタムコマンドを追加することもできます：

```python
from mcp_discord_notifier.discord_logger import DiscordLogger

logger = DiscordLogger(token, channel_id, thread_name)
await logger.start()

# カスタムコマンドを登録
async def my_command(message, args):
    await message.reply(f"Hello! Args: {args}")

logger.register_command(
    name="hello",
    handler=my_command,
    description="Say hello",
    usage="!hello [name]",
    category="Custom"
)
```

---

## VoiceVox統合

### セットアップ

1. **Docker Composeで起動**

```bash
docker-compose up -d
```

2. **動作確認**

```bash
# バージョン確認
curl http://localhost:50021/version

# スピーカー一覧
curl http://localhost:50021/speakers | jq

# 音声生成テスト
curl -X POST "http://localhost:50021/audio_query?text=こんにちは&speaker=1" > query.json
curl -X POST "http://localhost:50021/synthesis?speaker=1" \
  -H "Content-Type: application/json" \
  -d @query.json \
  --output test.wav
```

### GPU版を使用する場合

`docker-compose.yml`を編集：

```yaml
services:
  voicevox:
    image: voicevox/voicevox_engine:nvidia-ubuntu20.04-latest
    # ...
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

### スピーカー選択

VoiceVoxには複数の話者（声質）が用意されています：

| Speaker ID | 名前 | 説明 |
|------------|------|------|
| 1 | 四国めたん | 標準的な女性ボイス |
| 3 | ずんだもん | かわいらしい声 |
| 8 | 春日部つむぎ | 落ち着いた声 |
| 10 | 雨晴はう | 明るい声 |
| 11 | 波音リツ | クールな声 |

## トラブルシューティング

### MCPサーバーが起動しない

```bash
# インストール確認
which mcp-discord-notifier

# 環境変数確認
echo $DISCORD_TOKEN
echo $LOG_CHANNEL_ID

# 手動起動でエラー確認
mcp-discord-notifier --discord-token "YOUR_TOKEN" --log-channel-id YOUR_ID
```

### Discord接続エラー

**エラー**: "The connection with Discord is not ready"

**解決策:**
- Discordボットトークンが正しいか確認
- ボットがサーバーに招待されているか確認
- 必要な権限が付与されているか確認
- Message Content Intentが有効か確認

### スレッドが作成されない

**解決策:**
- チャンネルIDが正しいか確認（数値のみ）
- "Create Public Threads"権限があるか確認
- チャンネルがテキストチャンネルであることを確認

### VoiceVoxが動作しない

```bash
# コンテナ状態確認
docker-compose ps

# ログ確認
docker-compose logs voicevox

# 再起動
docker-compose restart voicevox

# 完全再起動
docker-compose down
docker-compose up -d
```

### 音声が再生されない

**確認事項:**
- FFmpegがインストールされているか
- ボットに"Connect"と"Speak"権限があるか
- ボイスチャンネルIDが正しいか
- VoiceVoxが起動しているか

```bash
# FFmpeg確認
ffmpeg -version

# VoiceVox確認
curl http://localhost:50021/version
```

## 開発

### ローカル開発

```bash
# リポジトリをクローン
git clone https://github.com/your-username/mcp-discord-notifier.git
cd mcp-discord-notifier

# 依存関係をインストール
uv sync

# 開発モードで実行
uv run mcp-discord-notifier \
  --discord-token "YOUR_TOKEN" \
  --log-channel-id YOUR_ID
```

### プロジェクト構造

```
mcp-discord-notifier/
├── src/
│   ├── __init__.py           # パッケージ初期化
│   ├── __main__.py           # エントリーポイント
│   ├── discord_logger.py     # Discord統合とTTS
│   ├── mcp_server.py         # MCPサーバー実装
│   └── voicevox_client.py    # VoiceVox APIクライアント
├── docs/
│   ├── MCP_CLIENT_SETUP.md   # MCPクライアント設定ガイド
│   └── PROMPT_TEMPLATES.md   # プロンプトテンプレート集
├── scripts/
│   ├── start.sh              # 起動スクリプト
│   └── stop.sh               # 停止スクリプト
├── docker-compose.yml        # VoiceVox Engine設定
├── pyproject.toml           # プロジェクト設定
├── CLAUDE.md                # AI開発アシスタント向けガイド
└── README.md                # このファイル
```

### テスト

プロジェクトには包括的なテストスイートが含まれています。

```bash
# ユニットテストを実行（推奨）
uv run pytest test/ -m "not integration and not manual" -v

# 統合テストを含む全テスト実行（手動テスト除く）
uv run pytest test/ -m "not manual" -v

# 特定のテストファイルを実行
uv run pytest test/test_settings.py -v
```

**テスト結果:**
```
✅ ユニットテスト:           47 passed (100%)
✅ 統合テスト (自動実行可能):  4 passed, 1 skipped
✅ 全テスト (手動除く):      51 passed, 1 skipped
```

詳細は [test/README.md](test/README.md) を参照してください。

**クイックテスト:**
```bash
# インポートテスト
uv run python -c "from src.discord_logger import DiscordLogger; print('OK')"

# VoiceVoxクライアントテスト
uv run python -c "
from src.voicevox_client import VoiceVoxClient
import asyncio

async def test():
    client = VoiceVoxClient()
    available = await client.is_available()
    print(f'VoiceVox available: {available}')

asyncio.run(test())
"
```

## ライセンス

MIT License - 詳細はLICENSEファイルを参照してください

## コントリビューション

コントリビューションを歓迎します！

1. このリポジトリをフォーク
2. フィーチャーブランチを作成（`git checkout -b feature/amazing-feature`）
3. 変更をコミット（`git commit -m 'Add amazing feature'`）
4. ブランチにプッシュ（`git push origin feature/amazing-feature`）
5. Pull Requestを作成

## 謝辞

このプロジェクトは以下のライブラリを使用しています：

- [mcp](https://github.com/modelcontextprotocol/python-sdk) - Python MCP SDK
- [discord.py](https://github.com/Rapptz/discord.py) - Discord APIライブラリ
- [VoiceVox Engine](https://github.com/VOICEVOX/voicevox_engine) - 日本語TTS
- [httpx](https://www.python-httpx.org/) - HTTP クライアント

## サポート

問題が発生した場合は、[GitHub Issues](https://github.com/your-username/mcp-discord-notifier/issues)で報告してください。

---

**作成者**: t-syunya (tsyunyam@gmail.com)
