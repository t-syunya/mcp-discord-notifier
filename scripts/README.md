# Scripts

このディレクトリには、MCP Discord Notifierを簡単に起動・停止するためのスクリプトが含まれています。

## スクリプトの用途

このMCPサーバーはDiscord Botと統合されているため、以下の2つの方法で起動できます：

### 起動方法の選択

#### 方法1: MCPクライアント経由（開発・個人利用）
MCPクライアント（Claude Code、Cursor等）に登録すると、クライアントが自動的にサーバーを起動・停止します。

**この方法が向いているケース：**
- 🧑‍💻 個人開発で使用
- 💻 MCPクライアント使用中のみBotを動かしたい
- 🔄 クライアント終了時にBotも停止したい

#### 方法2: 手動起動スクリプト（本番・常時利用）
これらのスクリプトを使用して、サーバーを常駐させます。

**この方法が向いているケース：**
- 🌐 Discord Botを常時稼働させたい
- 👥 複数人で使用する
- 📱 MCPクライアント起動前でも`!help`等のコマンドを使いたい
- 🖥️ サーバーとして運用したい

### スクリプトの使用場面

**必須の場合：**
- ✅ Discord Botコマンド（`!help`, `!join`, `!status`）を常時使いたい
- ✅ 複数のMCPクライアントから同時にアクセスしたい
- ✅ サーバーとして24時間稼働させたい

**任意の場合（MCPクライアント自動起動でもOK）：**
- 🔧 サーバーの動作確認
- 🐛 問題のデバッグ
- 📝 ログ出力の確認
- 🧪 VoiceVox統合のテスト

---

## 利用可能なスクリプト

### start.sh

MCP Discord Notifierを起動するスクリプト。VoiceVox EngineとMCPサーバーの起動を自動化します。

**使用方法:**
```bash
./scripts/start.sh
```

**処理内容:**
1. `.env`ファイルの確認と読み込み
2. 必須環境変数（DISCORD_TOKEN、LOG_CHANNEL_ID）のチェック
3. VoiceVox Engineの起動確認・起動
4. FFmpegのインストール確認
5. MCP Discord Notifierサーバーの起動

**前提条件:**
- プロジェクトルートに`.env`ファイルが存在すること
- `.env`に`DISCORD_TOKEN`と`LOG_CHANNEL_ID`が設定されていること

**オプション設定（.env）:**
- `DISCORD_TOKEN` (必須): Discordボットトークン
- `LOG_CHANNEL_ID` (必須): ログチャンネルID
- `LOG_THREAD_NAME` (任意): ログスレッド名（デフォルト: "Conversation Log"）
- `VOICE_CHANNEL_ID` (任意): 自動接続するボイスチャンネルID
- `VOICEVOX_URL` (任意): VoiceVox EngineのURL（デフォルト: http://localhost:50021）

---

### stop.sh

実行中のMCP Discord NotifierとVoiceVox Engineを停止するスクリプト。

**使用方法:**
```bash
./scripts/stop.sh [OPTIONS]
```

**オプション:**
- `--skip-voicevox`: VoiceVox Engineを停止しない
- `--force`: プロセスを強制終了（SIGKILL）
- `-h, --help`: ヘルプを表示

**例:**
```bash
# 通常の停止（VoiceVoxも停止）
./scripts/stop.sh

# VoiceVoxは停止せず、MCPサーバーのみ停止
./scripts/stop.sh --skip-voicevox

# 強制終了
./scripts/stop.sh --force
```

**処理内容:**
1. `mcp-discord-notifier`プロセスの検索と停止
2. VoiceVox Engine（Docker）の停止（オプション）
3. 必要に応じてコンテナの削除を確認

---

## トラブルシューティング

### .envファイルが見つからない

**エラー:**
```
⚠ .env ファイルが見つかりません
```

**解決方法:**
```bash
# プロジェクトルートで実行
cp .env.example .env
# .envファイルを編集してトークンとチャンネルIDを設定
```

### 必須設定が不足している

**エラー:**
```
⚠ DISCORD_TOKEN が設定されていません
⚠ LOG_CHANNEL_ID が設定されていません
```

**解決方法:**
`.env`ファイルを開いて、以下を設定：
```bash
DISCORD_TOKEN=your-discord-bot-token-here
LOG_CHANNEL_ID=1234567890123456789
```

### VoiceVoxが起動しない

**エラー:**
```
⚠ VoiceVox Engine の起動確認がタイムアウトしました
```

**解決方法:**
1. Dockerが起動しているか確認: `docker ps`
2. Docker Composeファイルが正しいか確認: `docker-compose config`
3. 手動でVoiceVoxを起動: `docker-compose up -d voicevox`
4. ログを確認: `docker-compose logs voicevox`

**注意:** VoiceVoxなしでも起動可能です。音声通知はテキストログにフォールバックします。

### FFmpegがインストールされていない

**警告:**
```
⚠ FFmpeg がインストールされていません
```

**解決方法:**
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows
# https://ffmpeg.org/download.html からダウンロード
```

### プロセスが停止しない

**症状:**
`stop.sh`を実行してもプロセスが残る

**解決方法:**
```bash
# 強制停止を使用
./scripts/stop.sh --force

# または手動でプロセスを確認・停止
ps aux | grep mcp-discord-notifier
kill -9 <PID>
```

---

## 開発者向け情報

### スクリプトの構造

両スクリプトは以下の構造で動作します：

```bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"
```

- `SCRIPT_DIR`: スクリプトが存在するディレクトリ（`scripts/`）
- `PROJECT_ROOT`: プロジェクトのルートディレクトリ
- 実行時はプロジェクトルートに移動して`.env`や`docker-compose.yml`にアクセス

### カスタマイズ

スクリプトは以下の方法でカスタマイズできます：

**起動前に追加処理を実行:**
```bash
# start.shの「MCPサーバーの起動」の前に追加
echo "カスタム処理を実行中..."
# your custom code here
```

**停止後に追加処理を実行:**
```bash
# stop.shの最後に追加
echo "クリーンアップ処理を実行中..."
# your custom code here
```

**色の定義を変更:**
```bash
# スクリプト内の色定義を編集
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'  # No Color
```

---

## 関連ドキュメント

- [CLAUDE.md](../CLAUDE.md) - プロジェクト全体のドキュメント
- [README.md](../README.md) - プロジェクト概要
- [test/README.md](../test/README.md) - テストドキュメント
