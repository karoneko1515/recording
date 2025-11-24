# 🎙️ オフライン自動議事録システム

**音声録音 → 文字起こし → 議事録生成** を完全オフラインで実行できる自動議事録システムです。

## 📋 主な機能

- **🔴 音声録音**: マイクから音声を録音してWAVファイルとして保存
- **📝 文字起こし**: Whisperで音声をテキスト化（日本語対応）
- **📄 議事録生成**: ローカルLLMで構造化された議事録を自動生成
- **🖥️ GUI**: Eel（WebベースUI）でシンプルな操作画面を提供

## 🛠️ 技術スタック

- **言語**: Python 3.9以上
- **音声認識**: [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (軽量版Whisper)
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

## 🚀 セットアップ手順

### 1. 必要な環境

- **Python**: 3.9以上
- **Ollama**: ローカルLLMの実行環境
- **マイク**: 音声録音用

### 2. リポジトリのクローン

```bash
git clone <このリポジトリのURL>
cd recording
```

### 3. Pythonライブラリのインストール

```bash
pip install -r requirements.txt
```

### 4. Ollamaのインストールと起動

#### Ollamaのインストール

公式サイトからインストール: https://ollama.ai/

または、以下のコマンドでインストール（Linux/macOS）:

```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

#### モデルのダウンロード

```bash
# Llama 3.1 8B（推奨、バランス型）
ollama pull llama3.1:8b

# または Qwen 2.5 7B（軽量、日本語特化）
ollama pull qwen2.5:7b
```

#### Ollamaの起動

```bash
ollama serve
```

> **注意**: Ollamaは別のターミナルで起動したまま保持してください。

### 5. 設定ファイルの編集（オプション）

`config.json` を編集して、モデルや設定をカスタマイズできます。

```json
{
  "whisper": {
    "model_size": "large-v3",  // Whisperモデル: tiny, base, small, medium, large-v2, large-v3
    "device": "cpu",           // デバイス: cpu, cuda
    "compute_type": "int8",    // 計算タイプ: int8, float16, float32
    "language": "ja"           // 言語: ja, en など
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

```
=== 文字起こし結果（タイムスタンプ付き） ===

[0:00:00 -> 0:00:05] 本日の会議を始めます。
[0:00:05 -> 0:00:12] まず、プロジェクトの進捗について報告します。
...

=== 文字起こし結果（テキストのみ） ===

本日の会議を始めます。
まず、プロジェクトの進捗について報告します。
...
```

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
