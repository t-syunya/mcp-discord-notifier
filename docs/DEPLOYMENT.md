# Deployment Guide

このガイドでは、MCP Discord Notifierを本番環境にデプロイする方法を説明します。

## 目次

- [デプロイ方法の選択](#デプロイ方法の選択)
- [方法1: systemdサービス（推奨）](#方法1-systemdサービス推奨)
- [方法2: Docker](#方法2-docker)
- [方法3: スクリーンセッション](#方法3-スクリーンセッション)
- [監視とログ](#監視とログ)
- [トラブルシューティング](#トラブルシューティング)

## デプロイ方法の選択

| 方法 | 難易度 | 自動再起動 | ログ管理 | おすすめ度 |
|-----|-------|----------|---------|----------|
| systemd | ⭐⭐ | ✅ | ✅ | ⭐⭐⭐⭐⭐ |
| Docker | ⭐⭐⭐ | ✅ | ✅ | ⭐⭐⭐⭐ |
| screen/tmux | ⭐ | ❌ | ❌ | ⭐⭐ |

## 方法1: systemdサービス（推奨）

Linuxサーバーで常駐サービスとして運用する標準的な方法です。

### 前提条件

- Linux OS（Ubuntu 20.04+, Debian 11+, CentOS 8+ など）
- sudo権限
- Python 3.12+
- uv インストール済み

### セットアップ手順

#### 1. アプリケーションのインストール

```bash
# 適切なディレクトリにクローン（例: /opt）
sudo mkdir -p /opt/mcp-discord-notifier
sudo chown $USER:$USER /opt/mcp-discord-notifier
cd /opt/mcp-discord-notifier

# リポジトリをクローン
git clone https://github.com/your-username/mcp-discord-notifier.git .

# 依存関係をインストール
uv sync
```

#### 2. 環境変数を設定

```bash
# .envファイルを作成
cp .env.example .env
nano .env
```

**.env の内容:**
```bash
DISCORD_TOKEN=your-bot-token-here
LOG_CHANNEL_ID=123456789012345678
LOG_THREAD_NAME=AI Conversation Log
VOICE_CHANNEL_ID=123456789012345678  # オプション
VOICEVOX_URL=http://localhost:50021
```

#### 3. systemdユニットファイルを作成

```bash
# サービスファイルをコピー
sudo cp scripts/mcp-discord-notifier.service /etc/systemd/system/

# サービスファイルを編集
sudo nano /etc/systemd/system/mcp-discord-notifier.service
```

**編集が必要な項目:**
- `User=YOUR_USERNAME` → 実行ユーザー名
- `Group=YOUR_GROUP` → 実行グループ名
- `WorkingDirectory=/path/to/mcp-discord-notifier` → 実際のパス
- `EnvironmentFile=/path/to/mcp-discord-notifier/.env` → 実際のパス
- `ReadWritePaths=/path/to/mcp-discord-notifier` → 実際のパス

#### 4. サービスを有効化・起動

```bash
# systemdをリロード
sudo systemctl daemon-reload

# サービスを有効化（起動時に自動起動）
sudo systemctl enable mcp-discord-notifier

# サービスを起動
sudo systemctl start mcp-discord-notifier

# ステータス確認
sudo systemctl status mcp-discord-notifier
```

#### 5. 動作確認

```bash
# ログを確認
sudo journalctl -u mcp-discord-notifier -f

# Discordでコマンドを実行
# !help, !status など
```

### サービス管理コマンド

```bash
# 起動
sudo systemctl start mcp-discord-notifier

# 停止
sudo systemctl stop mcp-discord-notifier

# 再起動
sudo systemctl restart mcp-discord-notifier

# ステータス確認
sudo systemctl status mcp-discord-notifier

# 自動起動を無効化
sudo systemctl disable mcp-discord-notifier

# ログ確認（リアルタイム）
sudo journalctl -u mcp-discord-notifier -f

# ログ確認（最新100行）
sudo journalctl -u mcp-discord-notifier -n 100
```

---

## 方法2: Docker

Dockerコンテナとして実行する方法です。

### Dockerfileの作成

```dockerfile
# Dockerfile
FROM python:3.12-slim

# 作業ディレクトリ
WORKDIR /app

# システム依存関係
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# uvをインストール
RUN pip install uv

# プロジェクトファイルをコピー
COPY . .

# 依存関係をインストール
RUN uv sync

# エントリーポイント
CMD ["uv", "run", "mcp-discord-notifier"]
```

### docker-compose.ymlの更新

既存の`docker-compose.yml`に追加：

```yaml
services:
  voicevox:
    # ... 既存の設定 ...

  mcp-discord-notifier:
    build: .
    container_name: mcp-discord-notifier
    restart: unless-stopped
    env_file:
      - .env
    depends_on:
      - voicevox
    networks:
      - default
    volumes:
      - ./logs:/app/logs
```

### 起動

```bash
# イメージをビルド
docker-compose build mcp-discord-notifier

# コンテナを起動
docker-compose up -d mcp-discord-notifier

# ログ確認
docker-compose logs -f mcp-discord-notifier
```

---

## 方法3: スクリーンセッション

シンプルだが手動管理が必要な方法です。

### スクリーンの使用

```bash
# スクリーンセッションを開始
screen -S mcp-discord-notifier

# アプリケーションを起動
cd /path/to/mcp-discord-notifier
./scripts/start.sh

# デタッチ（Ctrl+A, D）

# 再接続
screen -r mcp-discord-notifier

# セッション一覧
screen -ls
```

### tmuxの使用

```bash
# tmuxセッションを開始
tmux new -s mcp-discord-notifier

# アプリケーションを起動
cd /path/to/mcp-discord-notifier
./scripts/start.sh

# デタッチ（Ctrl+B, D）

# 再接続
tmux attach -t mcp-discord-notifier

# セッション一覧
tmux ls
```

**注意:** この方法は自動再起動やログ管理がないため、本番環境には推奨しません。

---

## 監視とログ

### systemdの場合

```bash
# リアルタイムログ
sudo journalctl -u mcp-discord-notifier -f

# エラーのみ表示
sudo journalctl -u mcp-discord-notifier -p err

# 特定期間のログ
sudo journalctl -u mcp-discord-notifier --since "2025-01-01" --until "2025-01-02"

# ログをファイルに出力
sudo journalctl -u mcp-discord-notifier > log.txt
```

### Dockerの場合

```bash
# リアルタイムログ
docker-compose logs -f mcp-discord-notifier

# 最新100行
docker-compose logs --tail=100 mcp-discord-notifier

# ログをファイルに出力
docker-compose logs mcp-discord-notifier > log.txt
```

### ログローテーション

大量のログが蓄積しないように設定：

```bash
# /etc/logrotate.d/mcp-discord-notifier
/var/log/mcp-discord-notifier/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0640 your-user your-group
    sharedscripts
    postrotate
        systemctl reload mcp-discord-notifier > /dev/null 2>&1 || true
    endscript
}
```

---

## 健全性チェック

### スクリプトの作成

```bash
#!/bin/bash
# scripts/healthcheck.sh

# MCP サーバーが応答しているか確認
# （実際のヘルスチェックエンドポイントに応じて調整）

if systemctl is-active --quiet mcp-discord-notifier; then
    echo "✅ Service is running"
    exit 0
else
    echo "❌ Service is not running"
    exit 1
fi
```

### cronで定期チェック

```bash
# crontabに追加
crontab -e

# 5分ごとにチェック
*/5 * * * * /path/to/mcp-discord-notifier/scripts/healthcheck.sh >> /var/log/mcp-healthcheck.log 2>&1
```

---

## トラブルシューティング

### サービスが起動しない

```bash
# 詳細なステータス確認
sudo systemctl status mcp-discord-notifier -l

# ログの確認
sudo journalctl -u mcp-discord-notifier -n 100 --no-pager

# 設定ファイルの検証
sudo systemd-analyze verify /etc/systemd/system/mcp-discord-notifier.service
```

**よくある原因:**
- `.env`ファイルのパスが間違っている
- 実行ユーザーに権限がない
- Python/uvのパスが正しくない
- ポートが既に使用されている

### Discord接続エラー

```bash
# トークンを確認
grep DISCORD_TOKEN /path/to/.env

# ネットワーク接続を確認
curl -I https://discord.com/api/v10

# ログでエラーメッセージを確認
sudo journalctl -u mcp-discord-notifier | grep -i error
```

### メモリ使用量が多い

```bash
# メモリ使用量を確認
sudo systemctl status mcp-discord-notifier | grep Memory

# プロセス詳細
ps aux | grep mcp-discord-notifier
```

**対策:**
- systemdサービスファイルに`MemoryMax=512M`等のリソース制限を追加
- VoiceVoxを別サーバーに分離

### 自動再起動が多い

```bash
# 再起動の履歴を確認
sudo journalctl -u mcp-discord-notifier | grep -i restart

# 失敗の理由を確認
sudo journalctl -u mcp-discord-notifier | grep -i failed
```

**対策:**
- `RestartSec`の値を増やす（デフォルト: 10s）
- `StartLimitBurst`を調整

---

## セキュリティのベストプラクティス

### 1. 環境変数の保護

```bash
# .envファイルのパーミッションを制限
chmod 600 /path/to/.env
chown your-user:your-group /path/to/.env
```

### 2. ファイアウォール設定

```bash
# UFW（Ubuntu）の場合
sudo ufw allow from 192.168.1.0/24 to any port 22
sudo ufw enable
```

### 3. 定期的な更新

```bash
# アプリケーションの更新
cd /path/to/mcp-discord-notifier
git pull
uv sync
sudo systemctl restart mcp-discord-notifier
```

### 4. バックアップ

```bash
# 設定ファイルのバックアップ
tar -czf mcp-discord-notifier-backup-$(date +%Y%m%d).tar.gz \
  /path/to/.env \
  /etc/systemd/system/mcp-discord-notifier.service
```

---

## パフォーマンスチューニング

### Python最適化

```bash
# 本番モードで実行（systemdサービスファイル）
Environment="PYTHONOPTIMIZE=1"
```

### リソース制限

systemdサービスファイルに追加：

```ini
[Service]
# CPU制限（50%）
CPUQuota=50%

# メモリ制限（512MB）
MemoryMax=512M

# プロセス数制限
TasksMax=128
```

---

## まとめ

**推奨デプロイ方法:**
1. **開発環境**: MCPクライアント経由の自動起動
2. **個人サーバー**: systemdサービス
3. **チーム利用**: systemdサービス + 監視
4. **大規模運用**: Docker + オーケストレーション

詳細は以下のドキュメントも参照してください：
- [README.md](../README.md) - 基本的な使い方
- [scripts/README.md](../scripts/README.md) - スクリプトの使い方
- [CLAUDE.md](../CLAUDE.md) - AI開発アシスタント向けガイド
