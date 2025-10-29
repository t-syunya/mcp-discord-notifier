# MCP Discord Notifier

AI開発アシスタント（Claude Code、Cursor、Codex等）がDiscordを通じてユーザーとインタラクティブにコミュニケーションできるMCP（Model Context Protocol）サーバーです。リアルタイム通知、ユーザーフィードバック、音声通知機能を提供します。

## 目次

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
- [VoiceVox統合](#voicevox統合)
- [トラブルシューティング](#トラブルシューティング)
- [開発](#開発)
- [ライセンス](#ライセンス)

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

#### 起動・停止スクリプトを使用（推奨）

**起動:**
```bash
# 1. .envファイルを作成
cp .env.example .env

# 2. .envファイルを編集して設定を入力
nano .env  # または好きなエディタで編集

# 3. サーバーを起動
./scripts/start.sh
```

起動スクリプトは以下を自動で行います：
- .envファイルの確認と読み込み
- 必須設定のバリデーション
- VoiceVox Engineの起動と待機
- FFmpegのインストール確認
- MCPサーバーの起動

**停止:**
```bash
# 通常の停止（MCPサーバーとVoiceVox Engineを停止）
./scripts/stop.sh

# VoiceVox Engineを起動したまま、MCPサーバーのみ停止
./scripts/stop.sh --skip-voicevox

# プロセスを強制終了
./scripts/stop.sh --force
```

#### コマンドラインから直接実行

pydantic-settingsが自動的に.envファイルから設定を読み込みます：

```bash
# .envファイルを作成・編集済みの場合
mcp-discord-notifier

# または環境変数で上書き
DISCORD_TOKEN="override-token" mcp-discord-notifier
```

#### Python モジュールとして実行

```bash
# uv を使用（.envから自動読み込み）
uv run mcp-discord-notifier

# または仮想環境をアクティベート後
source .venv/bin/activate
mcp-discord-notifier
```

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
✅ ユニットテスト:           32 passed (100%)
✅ 統合テスト (自動実行可能):  4 passed, 1 skipped
✅ 全テスト (手動除く):      36 passed, 1 skipped
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
