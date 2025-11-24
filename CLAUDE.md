# CLAUDE.md

このファイルは、このリポジトリで作業する際にAI開発アシスタント（Claude Code、Cursor、Codex等）にガイダンスを提供します。

## 開発ガイドライン

### Git コミットとプルリクエスト

このプロジェクトでは、**コミットメッセージとプルリクエストの本文は日本語で記述してください**。

#### コミットメッセージの形式

- **タイトル**: 英語の接頭辞 + 日本語の説明
- **本文**: 日本語で詳細を記述

**例:**
```
feat: CI ワークフローを並列ジョブに分割

単一の static-checks ジョブを3つの独立した並列ジョブに分割しました:
- format: Ruff フォーマットチェック
- lint: Ruff リントチェック
- type-check: Ty 型チェック

この変更により、CI の実行時間が短縮され、どのチェックが失敗したかを
明確に識別できるようになります。

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

#### プルリクエストの形式

- **タイトル**: コミットメッセージのタイトルと同じ形式
- **本文**: 日本語で以下を含める
  - **概要**: 変更内容の要約
  - **変更詳細**: 具体的な変更点
  - **テストプラン**: 検証方法のチェックリスト

### コード変更後の確認

コードを変更した後は、必ず以下のコマンドでチェックを実行してください:

```bash
make check
```

このコマンドは以下を順次実行します:
1. `make format` - Ruff でコードをフォーマット
2. `make lint` - Ruff でリントチェック
3. `make type-check` - Ty で型チェック

個別に実行することも可能です:
```bash
make format      # フォーマットのみ
make lint        # リントのみ
make type-check  # 型チェックのみ
```

利用可能なコマンドの一覧を表示:
```bash
make help
```

## プロジェクト概要

Discord Conversation Loggerは、AI開発アシスタント（Cursor、Codex、Claude Code等）がDiscordを通じてユーザーとインタラクティブにコミュニケーションするためのMCP（Model Context Protocol）サーバーです。

### 主な目的

1. **リアルタイム通知**: AIエージェントが進行状況や質問をDiscordに送信
2. **インタラクティブフィードバック**: Discordのリアクションによって作業続行の可否を決定
3. **ボイスチャンネル統合**: ボイスチャンネルに参加し、重要なイベントや応答待ち状態を音声で通知（テキスト埋め込みも同時送信）

### 技術スタック

- **言語**: Python 3.12+
- **Discord統合**: discord.py（voice対応）
- **MCP**: mcp Python SDK
- **非同期処理**: asyncio
- **パッケージ管理**: uv

### 開発状況

- ✅ 基本的なメッセージロギング機能
- ✅ カラーコード付き埋め込みメッセージ
- ✅ スレッド自動作成
- ✅ リアクションベースのワークフロー制御（`wait_for_reaction`ツール）
- ✅ ボイスチャンネル統合（基本実装、TTS未実装）
- ✅ 音声通知機能（VoiceVoxによるTTS再生とテキスト埋め込みを常時併用）

## コマンド

### 開発とインストール

**uv使用（推奨）:**
```bash
# プロジェクトのセットアップ（依存関係のインストールと仮想環境の作成）
uv sync

# ローカルで実行（環境変数または引数が必要）
uv run mcp-discord-notifier --log-channel-id YOUR_CHANNEL_ID --log-thread-name "Conversation Log"

# または仮想環境をアクティベート
source .venv/bin/activate  # Windows: .venv\Scripts\activate
mcp-discord-notifier --log-channel-id YOUR_CHANNEL_ID

# 環境変数を使用して実行
export DISCORD_TOKEN="your-bot-token"
export LOG_CHANNEL_ID="your-channel-id"
export LOG_THREAD_NAME="Conversation Log"
uv run mcp-discord-notifier

```

**pip使用（従来の方法）:**
```bash
# 開発モードでインストール
pip install -e .
```

### テストとリント

**テスト実行:**
```bash
# ユニットテストを実行（推奨）
uv run pytest test/ -m "not integration and not manual" -v

# 統合テストを含む全テスト実行（手動テスト除く）
uv run pytest test/ -m "not manual" -v

# カバレッジ付きで実行
uv run pytest test/ -m "not manual" --cov=src --cov-report=html
```

**テスト結果:**
```
✅ ユニットテスト:           47 passed (100%)
✅ 統合テスト (自動実行可能):  4 passed, 1 skipped
✅ 全テスト (手動除く):      51 passed, 1 skipped
```

詳細は [test/README.md](test/README.md) を参照。

**リント・フォーマット:**
```bash
# 型チェック（mypy がインストールされている場合）
uv run mypy src

# コードをフォーマット（black がインストールされている場合）
uv run black src

# リント（ruff がインストールされている場合）
uv run ruff check src
```

## アーキテクチャ

### モジュール構成

#### 現在の実装

コードベースは以下の主要なモジュールで構成されています：

1. **__main__.py** - エントリーポイントとMCPサーバーの初期化
   - argparseを使用してコマンドライン引数を解析（環境変数もサポート）
   - スレッド名に現在の作業ディレクトリを自動的に追加
   - asyncioを使用してDiscordクライアントとMCPサーバーを並行実行

2. **discord_logger.py** - Discordクライアントとロギング実装
   - `DiscordLogger`: discord.pyを使用したDiscord統合
   - 準備完了時にDiscordクライアントを初期化
   - スレッド管理: 最初のログメッセージで遅延的にスレッドを作成
   - 色分けされた埋め込み: human（青）、assistant（緑）、system（グレー）
   - リアクションベースのフィードバック機能
   - カスタムコマンド登録API

3. **command_handler.py** - Discordボットコマンドシステム
   - `CommandRegistry`: コマンド登録とルックアップ
   - `CommandHandler`: コマンドのパースと実行
   - デコレータベースのコマンド登録
   - エイリアス、カテゴリ、ヘルプメッセージのサポート
   - 組み込みコマンド: help, ping, status, thread, join, leave, say, speakers

4. **mcp_server.py** - MCPプロトコル統合
   - `ConversationLoggerServer`: `log_conversation`ツールを持つMCPサーバーハンドラー
   - Pydanticモデルを使用したリクエストバリデーション
   - MCP Python SDKを使用したプロトコル処理

5. **voicevox_client.py** - VoiceVox TTS統合
   - `VoiceVoxClient`: VoiceVox Engine APIクライアント
   - テキスト→音声変換
   - スピーカー一覧取得

6. **settings.py** - 設定管理
   - 環境変数からの設定読み込み
   - Pydanticベースのバリデーション

### 主要な設計パターン

- **クラスベース設計**: クラスにより異なるロギングバックエンドが可能（現在はDiscordのみ）
- **遅延初期化**: Discordスレッドは初回使用時に作成
- **非同期処理**: asyncio/awaitを使用した非同期実行
- **並行ランタイム**: DiscordクライアントとMCPサーバーが並行実行
- **コマンドレジストリパターン**: デコレータベースのコマンド登録により拡張可能
- **プラグインアーキテクチャ**: カスタムコマンドを実行時に動的に追加可能

### 設定

アプリケーションは以下の方法で設定を受け取ります：
1. コマンドライン引数: `--discord-token`、`--log-channel-id`、`--log-thread-name`
2. 環境変数: `DISCORD_TOKEN`、`LOG_CHANNEL_ID`、`LOG_THREAD_NAME`
3. セットアップ用のヘルパースクリプト:
   - `setup-discord-env.sh`: 設定テンプレートを`~/.claude/discord-config.json`にコピー
   - `load-discord-env.sh`: JSONから設定を読み込み環境変数としてエクスポート（`jq`が必要）

## MCP統合

### 現在のツール

#### log_conversation

メッセージをDiscordに送信するための基本ツール：

```json
{
  "role": "human" | "assistant" | "system",
  "message": "メッセージ内容",
  "context": "オプションのコンテキストメタデータ"
}
```

**使用例:**
- 作業開始/完了の通知
- ユーザーへの質問
- エラーや警告の報告
- 進捗状況の更新

#### wait_for_reaction

送信したメッセージへのリアクションを待ち、ユーザーのフィードバックに基づいて処理を継続：

```json
{
  "message": "確認メッセージ",
  "options": ["✅ 承認", "❌ 拒否", "⏸️ 一時停止"],
  "timeout": 300,  // 秒（デフォルト: 300）
  "context": "オプションのコンテキスト"
}
```

**使用例:**
- 重要な変更前のユーザー承認
- 複数の選択肢からの意思決定
- 処理の一時停止/継続の判断
- デプロイやリリース前の最終確認

**戻り値:**
```json
{
  "emoji": "✅",
  "option": "✅ 承認",
  "user": "ユーザー名#1234",
  "message_id": 123456789
}
```

#### notify_voice

ボイスチャンネルで音声通知を行う：

```json
{
  "voice_channel_id": 123456789,
  "message": "音声で読み上げるメッセージ",
  "priority": "normal",  // "normal" または "high"
  "speaker_id": 1  // VoiceVoxスピーカーID（デフォルト: 1 = 四国めたん ノーマル）
}
```

**使用例:**
- 長時間タスクの完了通知
- 緊急の問題やエラーの通知
- ユーザーが離席中の重要な更新

**VoiceVox統合:**
- VoiceVox Engineがhttp://localhost:50021で利用可能な場合、実際のTTSを使用
- VoiceVoxが利用できない場合はエラーとして扱われ、音声通知は実行されません
- Dockerで簡単にセットアップ可能（`docker-compose up -d`）

**スピーカーID一覧（主要なもの）:**
- 1: 四国めたん（ノーマル）
- 3: ずんだもん（ノーマル）
- 8: 春日部つむぎ（ノーマル）
- 他多数（VoiceVox APIで確認可能）

### 各AI開発アシスタントへの追加方法

#### Claude Code

```bash
# 設定から環境変数を読み込み
source ./load-discord-env.sh

# MCPサーバーをグローバルに追加
claude mcp add -s user mcp-discord-notifier mcp-discord-notifier \
  -e DISCORD_TOKEN="$DISCORD_TOKEN" \
  -- --log-channel-id "$LOG_CHANNEL_ID" --log-thread-name "$LOG_THREAD_NAME"

# または現在のプロジェクトにローカルで追加
claude mcp add mcp-discord-notifier mcp-discord-notifier \
  -e DISCORD_TOKEN="$DISCORD_TOKEN" \
  -- --log-channel-id "$LOG_CHANNEL_ID" --log-thread-name "$LOG_THREAD_NAME"
```

#### Cursor / その他のMCP対応エディタ

MCP設定ファイル（通常は`~/.cursor/mcp.json`または`~/.claude.json`）に以下を追加：

```json
{
  "mcpServers": {
    "mcp-discord-notifier": {
      "command": "mcp-discord-notifier",
      "args": [
        "--log-channel-id", "YOUR_CHANNEL_ID",
        "--log-thread-name", "AI Conversation Log"
      ],
      "env": {
        "DISCORD_TOKEN": "YOUR_DISCORD_BOT_TOKEN"
      }
    }
  }
}
```

または環境変数を使用：

```json
{
  "mcpServers": {
    "mcp-discord-notifier": {
      "command": "bash",
      "args": [
        "-c",
        "source ~/.claude/load-discord-env.sh && mcp-discord-notifier --log-channel-id \"$LOG_CHANNEL_ID\" --log-thread-name \"$LOG_THREAD_NAME\""
      ]
    }
  }
}
```

#### Codex（OpenAI）

CodexはMCPをサポートしています。設定は`~/.codex/config.toml`に保存され、CLIとIDE拡張機能の両方で共有されます。

**方法1: CLIを使用（推奨）**

```bash
# 設定から環境変数を読み込み
source ./load-discord-env.sh

# MCPサーバーを追加
codex mcp add mcp-discord-notifier \
  --env DISCORD_TOKEN="$DISCORD_TOKEN" \
  --env LOG_CHANNEL_ID="$LOG_CHANNEL_ID" \
  --env LOG_THREAD_NAME="$LOG_THREAD_NAME" \
  -- mcp-discord-notifier
```

**方法2: config.tomlを直接編集**

`~/.codex/config.toml`に以下を追加：

```toml
[mcp_servers.mcp-discord-notifier]
command = "mcp-discord-notifier"
args = [
  "--log-channel-id", "YOUR_CHANNEL_ID",
  "--log-thread-name", "AI Conversation Log"
]

[mcp_servers.mcp-discord-notifier.env]
DISCORD_TOKEN = "YOUR_DISCORD_BOT_TOKEN"
```

**設定の確認**

Codex CLIで`codex`を起動し、`/mcp`と入力してMCPサーバーの状態を確認できます。

**Tips:**
- 設定はCLIとIDE拡張機能で共有されるため、一度設定すれば両方で使用可能
- `codex mcp list`で現在設定されているMCPサーバーの一覧を表示
- `codex mcp remove mcp-discord-notifier`でサーバーを削除
- 環境変数は`[mcp_servers.<server-name>.env]`テーブルに記述

## Discordボットコマンド

ログチャンネルでボットに対してコマンドを実行できます。すべてのコマンドは `!` で始まります。

### 情報コマンド

#### !help [command]
利用可能なコマンドの一覧を表示します。特定のコマンド名を指定すると、そのコマンドの詳細なヘルプを表示します。

**エイリアス**: `!h`, `!?`

**使用例**:
```
!help           # 全コマンド一覧
!help ping      # pingコマンドの詳細
!h              # エイリアスでも可
```

#### !ping
ボットのレイテンシー（応答速度）を確認します。

**使用例**:
```
!ping
```

#### !status
ボットの現在の状態を表示します：
- ボット情報
- レイテンシー
- ログスレッド
- ボイスチャンネル接続状態
- VoiceVox Engine の状態

**エイリアス**: `!info`

**使用例**:
```
!status
!info
```

### 管理コマンド

#### !thread [name]
新しいログスレッドを作成します。名前を指定すると、そのスレッド名で作成されます。

**使用例**:
```
!thread                    # デフォルト名で新規作成
!thread New Feature Work   # 指定した名前で作成
```

### ボイスコマンド

#### !join [voice_channel_id]
ボイスチャンネルに接続します。チャンネルIDを省略した場合、環境変数で設定されたデフォルトチャンネルに接続します。

**使用例**:
```
!join                      # デフォルトチャンネルに接続
!join 123456789012345678   # 指定したチャンネルに接続
```

**Tips**: チャンネルIDの取得方法
1. Discordの設定で開発者モードを有効化
2. ボイスチャンネルを右クリック
3. 「IDをコピー」を選択

#### !leave
現在接続中のボイスチャンネルから切断します。

**エイリアス**: `!disconnect`

**使用例**:
```
!leave
!disconnect
```

#### !say <message>
接続中のボイスチャンネルでメッセージを音声読み上げします（VoiceVox が必要）。

**エイリアス**: `!speak`, `!tts`

**使用例**:
```
!say こんにちは
!speak テストが完了しました
!tts ビルドに成功しました
```

#### !speakers
VoiceVox Engine で利用可能な音声スピーカーの一覧を表示します。

**使用例**:
```
!speakers
```

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
    category="Custom",
    aliases=["hi", "greet"]
)
```

## Discordセットアップ要件

Discordボットには以下の権限が必要です：
- Send Messages（メッセージの送信）
- Create Public Threads（公開スレッドの作成）
- Read Message History（メッセージ履歴の読み取り）
- Embed Links（埋め込みリンク）

そして以下の特権インテント：
- Message Content Intent（メッセージコンテンツインテント）

## 開発ノート

### 依存関係
- **mcp**: MCPプロトコル実装（Python SDK）
- **discord.py**: Discord APIクライアント（v2.3以上）
- **pydantic**: データバリデーションとスキーマ生成
- **asyncio**: 非同期処理（Python標準ライブラリ）

### スレッド命名
スレッド名には現在の作業ディレクトリが自動的に含まれます：
- フォーマット: `{LOG_THREAD_NAME} [{cwd}]`
- 例: `"Conversation Log [/home/user/project]"`
- これにより、ログがどのプロジェクトコンテキストに属するかを識別できます

### エラーハンドリング
- Discordエラーは例外として伝播
- MCPツールエラーは`RuntimeError`としてラップ
- DiscordまたはMCP接続のいずれかが失敗するとサーバーは終了

## トラブルシューティング

### MCPサーバーが起動しない場合

1. **バイナリがインストールされているか確認**
   ```bash
   which mcp-discord-notifier
   ```

2. **環境変数が正しく設定されているか確認**
   ```bash
   echo $DISCORD_TOKEN
   echo $LOG_CHANNEL_ID
   ```

3. **手動でサーバーを起動してエラーメッセージを確認**
   ```bash
   export DISCORD_TOKEN="your-token"
   export LOG_CHANNEL_ID="your-channel-id"
   mcp-discord-notifier
   ```

### "The connection with Discord is not ready"エラー

- Discordボットトークンが正しいか確認
- ボットが対象のサーバーに招待されているか確認
- 必要な権限とインテントが有効になっているか確認（上記「Discordセットアップ要件」参照）

### スレッドが作成されない

- チャンネルIDが正しいか確認（数値のみ、引用符なし）
- ボットに「Create Public Threads」権限があるか確認
- チャンネルがスレッド作成可能なタイプ（テキストチャンネル）であるか確認

### Codex固有の問題

- `codex mcp list`でサーバーが正しく登録されているか確認
- `~/.codex/config.toml`の構文エラーをチェック（TOMLフォーマット）
- Codexを再起動して設定を再読み込み

---

## このプロジェクトでMCP Discord Notifierを使用する

このプロジェクトの開発中に、MCP Discord Notifierを使用して作業進捗をDiscordに通知できます。

### 設定情報

- **MCPサーバー**: mcp-discord-notifier
- **プロジェクトパス**: `/mnt/l/WSL/Projects/mcp-discord-notifier`
- **実行コマンド**: `uv run mcp-discord-notifier`
- **環境変数**: プロジェクトルートの `.env` ファイルから自動読み込み

### Claude Codeでの設定

このプロジェクトのローカルMCP設定を追加：

```bash
# プロジェクトディレクトリで実行
cd /mnt/l/WSL/Projects/mcp-discord-notifier

# ローカル設定を追加
claude mcp add mcp-discord-notifier \
  -- bash -c "cd /mnt/l/WSL/Projects/mcp-discord-notifier && uv run mcp-discord-notifier"
```

### 利用可能なツール

#### 1. log_conversation
作業の進捗や考えをDiscordに記録：

```jsonc
{
  "role": "assistant",  // "human" | "assistant" | "system"
  "message": "テストの追加が完了しました。全36テストがパスしています。",
  "context": "feat/add-tests-and-docs"  // オプション
}
```

#### 2. wait_for_reaction
重要な判断でユーザーの確認を待つ：

```jsonc
{
  "message": "既存のテストを全て上書きしますか？",
  "options": ["✅ 続行", "❌ 中止", "⏸️ 後で"],
  "timeout": 300  // 秒
}
```

#### 3. notify_voice
長時間タスクの完了を音声で通知：

```jsonc
{
  "voice_channel_id": 1356518373097214022,
  "message": "ビルドとテストが完了しました",
  "priority": "high",  // "normal" | "high"
  "speaker_id": 1  // VoiceVox speaker ID
}
```

### 音声通知を使用する場合

1. **ボイスチャンネルに接続**:
   Discordのログチャンネルで `!join` コマンドを実行

2. **音声通知を送信**:
   AIアシスタントに自然言語で依頼：
   - 「テストが完了したら音声で教えて」
   - 「ビルドエラーが出たら声で警告して」

3. **切断**:
   Discordで `!leave` コマンドを実行

### 使用が推奨される場面

以下の場面では**積極的にMCPツールを使用**してください：

#### log_conversation を使用
- **作業開始時**: 「〜の実装を開始します」
- **作業完了時**: 「〜が完了しました」
- **問題発見時**: 「〜でエラーが発生しています」
- **考えや気づき**: 「〜という方法も検討できます」

#### wait_for_reaction を使用
- **破壊的変更前**: 「既存のコードを削除します」
- **重要な判断**: 「アプローチAとBがあります」
- **長時間タスク前**: 「この処理には時間がかかります」

#### notify_voice を使用
- **長時間ビルド完了**: 「ビルドが完了しました」
- **テスト完了**: 「全テストがパスしました」
- **エラー発生**: 「エラーが発生しました」

### 使用制限

- mcp-discord-notifierは**制限なく**いつでも利用可能です
- 作業の進捗、発見、困っていること、考えていることなど、**自由に発言**してください
- ユーザーとのコミュニケーションを円滑にするため、積極的に活用してください

## 自動音声通知ルール

このプロジェクトでは、以下の実行関連イベントで**自動的に音声通知を行う**ようにしてください：

### 必須通知イベント

#### 1. テスト実行完了
テストコマンド（`pytest`, `make test` など）を実行した後、結果を音声で通知：

```python
# テスト実行後
notify_voice(
    voice_channel_id=1356518373097214022,
    message=f"テストが完了しました。{passed}件成功、{failed}件失敗です。",
    priority="normal" if failed == 0 else "high",
    speaker_id=1  # 四国めたん
)
```

#### 2. ビルド/チェック完了
`make check`, `make build` などのビルド関連コマンド実行後：

```python
# ビルド成功時
notify_voice(
    voice_channel_id=1356518373097214022,
    message="ビルドとチェックが完了しました。エラーはありません。",
    priority="normal",
    speaker_id=1  # 四国めたん
)

# ビルド失敗時
notify_voice(
    voice_channel_id=1356518373097214022,
    message="ビルドでエラーが発生しました。確認してください。",
    priority="high",
    speaker_id=1  # 四国めたん
)
```

#### 3. 長時間タスク完了
実行時間が30秒以上かかるコマンドの完了時：

```python
notify_voice(
    voice_channel_id=1356518373097214022,
    message="長時間タスクが完了しました。",
    priority="normal",
    speaker_id=1
)
```

#### 4. エラー発生
コマンド実行中にエラーが発生した場合：

```python
notify_voice(
    voice_channel_id=1356518373097214022,
    message="エラーが発生しました。詳細を確認してください。",
    priority="high",
    speaker_id=1  # 四国めたん
)
```

### 通知のタイミング

1. **実行前**: `log_conversation` でタスク開始をログ
2. **実行中**: 長時間タスクの場合、進捗を定期的にログ
3. **実行後**:
   - `log_conversation` で結果の詳細をログ
   - `notify_voice` で音声通知（**必須**）

### 実装例

```python
# 例: テスト実行フロー
async def run_tests():
    # 1. 開始をログ
    log_conversation(
        role="assistant",
        message="テストを実行します...",
        context="test-execution"
    )

    # 2. テスト実行
    result = subprocess.run(["pytest", "test/"])

    # 3. 結果をログ
    log_conversation(
        role="assistant",
        message=f"テスト完了: {result.returncode == 0 and '成功' or '失敗'}",
        context="test-result"
    )

    # 4. 音声通知（必須）
    notify_voice(
        voice_channel_id=1356518373097214022,
        message=f"テストが完了しました。結果: {result.returncode == 0 and '成功' or '失敗'}",
        priority="high" if result.returncode != 0 else "normal",
        speaker_id=1  # 四国めたん
    )
```

### スピーカー選択ガイドライン

- **speaker_id=1** (四国めたん): **デフォルト** - 全ての通知で使用
- **speaker_id=3** (ずんだもん): 必要に応じて使用可能
- **speaker_id=8** (春日部つむぎ): 必要に応じて使用可能

### 音声設定

- **話速**: デフォルトで1.2倍速（通常より少し早め）に設定済み
- VoiceVoxClientで自動的に適用されます

### 注意事項

- **VoiceVox Engine が起動していない場合**: 音声再生は失敗として扱われます（テキスト通知は送信されますが、必ずVoiceVoxを起動してください）
- **Discord Bot Daemon が起動していない場合**: エラーが発生するため、事前に `./scripts/start.sh` で起動してください
- **音声通知は必須**: ユーザーが通話中の場合、リアルタイムで作業状況を把握できるため、必ず実行してください

### トラブルシューティング

#### MCPサーバーが起動しない
```bash
# 手動で起動して確認
cd /mnt/l/WSL/Projects/mcp-discord-notifier
uv run mcp-discord-notifier

# .env ファイルを確認
cat .env
```

#### ツールが表示されない
```bash
# Claude Codeの設定を確認
claude mcp list

# 設定を削除して再追加
claude mcp remove mcp-discord-notifier
claude mcp add mcp-discord-notifier \
  -- bash -c "cd /mnt/l/WSL/Projects/mcp-discord-notifier && uv run mcp-discord-notifier"
```
