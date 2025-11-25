# 🎙️ オフライン自動議事録システム

**音声録音 → 文字起こし → 議事録生成** を完全オフラインで実行できる自動議事録システムです。

## 📋 主な機能

- **🔴 音声録音**: マイクから音声を録音してWAVファイルとして保存
- **📝 文字起こし**: WhisperX で音声をテキスト化（日本語対応）
- **👥 話者識別**: 誰が発言したかを自動的に識別（Speaker Diarization）
- **📄 議事録生成**: ローカルLLMで構造化された議事録を自動生成
- **🖥️ GUI**: Eel（WebベースUI）でシンプルな操作画面を提供

## 🛠️ 技術スタック

- **言語**: Python 3.9以上
- **音声認識**: [WhisperX](https://github.com/m-bain/whisperX) (faster-whisper拡張版)
- **話者識別**: [pyannote.audio](https://github.com/pyannote/pyannote-audio) (Speaker Diarization)
- **LLM**: [Ollama](https://ollama.ai/) + Llama 3.1 8B または Qwen 2.5 7B
- **GUI**: Eel（HTML/CSS/JavaScript + Python）
- **音声録音**: sounddevice + scipy

## 📁 ファイル構成

```
recording/
├── main.py              # メインアプリケーション（Eelバックエンド）
├── recorder.py          # 音声録音モジュール
├── transcriber.py       # Whisperによる文字起こしモジュール
├── summarizer.py        # Ollamaによる議事録生成モジュール
├── config.json          # 設定ファイル
├── requirements.txt     # 依存ライブラリ
├── web/                 # Webフロントエンド
│   ├── index.html       # メインUI
│   ├── style.css        # スタイルシート
│   └── script.js        # JavaScript
└── output/              # 出力ディレクトリ（自動作成）
    ├── recording_*.wav  # 録音ファイル
    ├── transcript_*.txt # 文字起こしファイル
    └── minutes_*.md     # 議事録ファイル
```

## 🚀 セットアップ手順（完全版）

### ステップ1: 必要な環境の確認

以下がインストールされているか確認してください：

- **Git**: バージョン管理ツール
- **Python**: 3.9以上
- **pip**: Pythonパッケージマネージャー（Pythonに付属）
- **マイク**: 音声録音用のデバイス

### ステップ2: Gitリポジトリのクローン

#### GitHubからクローン

```bash
# HTTPSでクローン（推奨）
git clone https://github.com/karoneko1515/recording.git

# またはSSHでクローン（SSH鍵を設定済みの場合）
git clone git@github.com:karoneko1515/recording.git

# リポジトリディレクトリに移動
cd recording
```

> **注意**: リポジトリURLは実際のGitHubリポジトリURLに置き換えてください。

#### Gitがインストールされていない場合

**Windows:**
- [Git for Windows](https://gitforwindows.org/) からダウンロードしてインストール

**macOS:**
```bash
# Homebrewを使用
brew install git

# またはXcode Command Line Toolsをインストール
xcode-select --install
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install git
```

**Linux (CentOS/RHEL):**
```bash
sudo yum install git
```

### ステップ3: Python環境のセットアップ

#### Pythonのバージョン確認

```bash
python --version
# または
python3 --version
```

Python 3.9以上がインストールされていることを確認してください。

#### Python仮想環境の作成（推奨）

```bash
# 仮想環境を作成
python -m venv venv

# 仮想環境を有効化
# Windows (コマンドプロンプト)
venv\Scripts\activate.bat

# Windows (PowerShell)
venv\Scripts\Activate.ps1

# macOS / Linux
source venv/bin/activate
```

#### 依存ライブラリのインストール

```bash
pip install -r requirements.txt
```

> **注意**: インストールには数分かかる場合があります。

### ステップ4: Ollamaのインストールと設定

#### 4-1. Ollamaのインストール

**Windows:**

1. [Ollama公式サイト](https://ollama.ai/) にアクセス
2. "Download for Windows" をクリック
3. ダウンロードした `OllamaSetup.exe` を実行
4. インストールウィザードに従ってインストール

**macOS:**

方法1: 公式サイトからダウンロード
1. [Ollama公式サイト](https://ollama.ai/) にアクセス
2. "Download for Mac" をクリック
3. ダウンロードした `.dmg` ファイルを開いてインストール

方法2: Homebrewを使用
```bash
brew install ollama
```

**Linux (Ubuntu/Debian/CentOS/RHEL):**

```bash
# 自動インストールスクリプト（推奨）
curl -fsSL https://ollama.ai/install.sh | sh
```

手動インストール（詳細は [公式ドキュメント](https://github.com/ollama/ollama/blob/main/docs/linux.md) を参照）

#### 4-2. Ollamaの起動

**Windows:**
- インストール後、Ollamaは自動的にバックグラウンドで起動します
- タスクトレイにOllamaアイコンが表示されます

**macOS:**
- アプリケーションフォルダからOllamaを起動
- メニューバーにOllamaアイコンが表示されます

**Linux:**
```bash
# ターミナルで起動（別のターミナルウィンドウで実行）
ollama serve
```

> **重要**: Linuxの場合、Ollamaは別のターミナルウィンドウで起動したまま保持してください。

#### 4-3. Ollamaが起動しているか確認

```bash
# Ollamaのバージョンを確認
ollama --version

# 実行中のモデルを確認
ollama list
```

#### 4-4. LLMモデルのダウンロード

```bash
# Llama 3.1 8B（推奨、バランス型）約4.7GB
ollama pull llama3.1:8b

# または Qwen 2.5 7B（軽量、日本語特化）約4.4GB
ollama pull qwen2.5:7b
```

> **注意**: モデルのダウンロードには時間がかかります（数分〜数十分）。
> 初回のみ必要で、2回目以降は不要です。

#### 4-5. モデルの動作確認

```bash
# Llama 3.1でテスト
ollama run llama3.1:8b "こんにちは"

# 終了するには /bye と入力
```

### ステップ5: Hugging Face Tokenの取得（話者識別機能を使う場合）

話者識別機能を使用するには、Hugging Face Tokenが必要です。

#### 5-1. Hugging Faceアカウントの作成

1. [Hugging Face](https://huggingface.co/) にアクセス
2. "Sign Up" をクリックしてアカウントを作成（無料）

#### 5-2. Tokenの取得

1. ログイン後、右上のプロフィールアイコン → "Settings" をクリック
2. 左メニューから "Access Tokens" を選択
3. "New token" をクリック
4. Token名を入力（例: "ollama-meeting-minutes"）
5. Role は "Read" を選択
6. "Generate token" をクリック
7. 表示されたTokenをコピー（一度しか表示されません）

#### 5-3. pyannote.audioモデルへのアクセス許可

1. [pyannote/speaker-diarization](https://huggingface.co/pyannote/speaker-diarization) にアクセス
2. "Agree and access repository" をクリック
3. [pyannote/segmentation](https://huggingface.co/pyannote/segmentation) にも同様にアクセス許可

#### 5-4. Tokenを設定ファイルに追加

`config.json` の `hf_token` にTokenを貼り付けます：

```json
{
  "diarization": {
    "enabled": true,
    "min_speakers": 1,
    "max_speakers": 10,
    "hf_token": "ここに取得したTokenを貼り付け"
  }
}
```

### ステップ6: 設定ファイルの編集（オプション）

`config.json` を編集して、モデルや設定をカスタマイズできます。

```json
{
  "whisper": {
    "model_size": "large-v3",  // Whisperモデル: tiny, base, small, medium, large-v2, large-v3
    "device": "cpu",           // デバイス: cpu, cuda
    "compute_type": "int8",    // 計算タイプ: int8, float16, float32
    "language": "ja",          // 言語: ja, en など
    "use_whisperx": true       // WhisperXを使用（話者識別対応）
  },
  "diarization": {
    "enabled": true,           // 話者識別を有効化
    "min_speakers": 1,         // 最小話者数
    "max_speakers": 10,        // 最大話者数
    "hf_token": ""             // Hugging Face Token（必須）
  },
  "ollama": {
    "model": "llama3.1:8b",              // Ollamaモデル名
    "base_url": "http://localhost:11434" // OllamaのURL
  },
  "recording": {
    "sample_rate": 16000,  // サンプリングレート（Hz）
    "channels": 1          // チャンネル数（1=モノラル）
  },
  "output": {
    "directory": "output"  // 出力ディレクトリ
  }
}
```

## ▶️ 使い方

### アプリケーションの起動

```bash
python main.py
```

ブラウザが自動的に開き、Webベースのユーザーインターフェースが表示されます。

### 操作手順

1. **🔴 録音開始**: マイクから音声の録音を開始します。
2. **⏹️ 録音停止**: 録音を停止してWAVファイルとして保存します。
3. **📝 文字起こし実行**: 録音した音声をWhisperで文字起こしします。
4. **📄 議事録生成**: 文字起こしテキストからOllamaで議事録を生成します。
5. **💾 保存**: 文字起こしや議事録をファイルとして保存できます。

## 📤 出力形式

### 文字起こしテキスト（`.txt`）

**話者識別付き（WhisperX使用時）:**

```
=== 文字起こし結果（話者識別付き） ===

[0:00:00 -> 0:00:05] SPEAKER_00: 本日の会議を始めます。
[0:00:05 -> 0:00:12] SPEAKER_01: まず、プロジェクトの進捗について報告します。
[0:00:12 -> 0:00:25] SPEAKER_00: ありがとうございます。現在の状況はどうですか？
[0:00:25 -> 0:00:40] SPEAKER_02: スケジュール通りに進んでいます。
...

=== 文字起こし結果（テキストのみ） ===

本日の会議を始めます。
まず、プロジェクトの進捗について報告します。
ありがとうございます。現在の状況はどうですか？
スケジュール通りに進んでいます。
...
```

> **注**: SPEAKER_00, SPEAKER_01... は自動的に識別された話者です。議事録生成時にLLMが参加者名を推測することがあります。

### 議事録（`.md` Markdown形式）

```markdown
# 議事録

## 日時
2025年01月24日

## 参加者
- 田中さん
- 佐藤さん

## 議題
- プロジェクトの進捗報告
- 次のマイルストーンの確認

## 議論内容
...

## 決定事項
- 次回ミーティングは来週水曜日
- ...

## TODO・アクションアイテム
- [ ] 田中さん: 資料の準備
- [ ] 佐藤さん: テスト環境の構築

## 補足・備考
...
```

## ⚙️ トラブルシューティング

### Q1. Ollamaに接続できません

**A**: Ollamaが起動しているか確認してください。

```bash
ollama serve
```

別のターミナルで起動したまま保持してください。

### Q2. faster-whisperのモデルダウンロードが遅い

**A**: 初回実行時は、Whisperモデル（約3GB）を自動ダウンロードします。時間がかかる場合がありますが、2回目以降は高速に動作します。

### Q3. マイクが認識されません

**A**: 利用可能な音声デバイスを確認してください。

```bash
python -c "import sounddevice as sd; print(sd.query_devices())"
```

### Q4. 文字起こしの精度が低い

**A**: Whisperモデルのサイズを変更してください。

- `config.json` の `whisper.model_size` を `large-v3`（高精度）または `medium`（バランス）に設定してください。

### Q5. 議事録生成が遅い

**A**: Ollamaのモデルを軽量化するか、GPUを使用してください。

- 軽量モデル: `qwen2.5:7b` または `llama3.1:8b`
- GPU使用: CUDAをインストールし、`config.json` の `whisper.device` を `cuda` に変更

## 📊 推奨スペック

### 最小スペック
- **CPU**: Intel Core i5 以上
- **RAM**: 8GB 以上
- **ストレージ**: 10GB 以上（モデルデータ用）

### 推奨スペック
- **CPU**: Intel Core i7 / Ryzen 7 以上
- **RAM**: 16GB 以上
- **GPU**: CUDA対応GPU（NVIDIA）
- **ストレージ**: 20GB 以上

## 🔧 開発者向け情報

### モジュール構成

- `recorder.py`: sounddeviceを使用して音声録音
- `transcriber.py`: faster-whisperで音声をテキスト化
- `summarizer.py`: Ollama APIで議事録を生成
- `main.py`: Eelで各モジュールを統合

### カスタマイズ

#### 議事録フォーマットの変更

`summarizer.py` の `_create_prompt()` メソッドでプロンプトを編集できます。

#### UI の変更

`web/` ディレクトリ内のHTML/CSS/JavaScriptを編集してUIをカスタマイズできます。

## 📝 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 🙏 謝辞

- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) - 高速なWhisper実装
- [Ollama](https://ollama.ai/) - ローカルLLMの実行環境
- [Eel](https://github.com/python-eel/Eel) - PythonとJavaScriptの統合フレームワーク

## 📞 サポート

問題や質問がある場合は、GitHubのIssuesセクションで報告してください。

---

**Powered by Whisper (faster-whisper) + Ollama**
