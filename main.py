"""
メインアプリケーション
Eelを使用してWebベースのGUIを提供します。
"""

import eel
import json
import os
import sys
from recorder import AudioRecorder
from transcriber import Transcriber
from summarizer import MinutesSummarizer

# グローバル変数
recorder = None
transcriber = None
summarizer = None
config = None


def load_config():
    """設定ファイルを読み込み"""
    global config

    config_file = "config.json"

    if not os.path.exists(config_file):
        print(f"警告: 設定ファイル '{config_file}' が見つかりません。デフォルト設定を使用します。")
        config = {
            "whisper": {
                "model_size": "large-v3",
                "device": "cpu",
                "compute_type": "int8",
                "language": "ja"
            },
            "ollama": {
                "model": "llama3.1:8b",
                "base_url": "http://localhost:11434"
            },
            "recording": {
                "sample_rate": 16000,
                "channels": 1
            },
            "output": {
                "directory": "output"
            }
        }
        return

    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
        print("設定ファイルを読み込みました")
    except Exception as e:
        print(f"エラー: 設定ファイルの読み込みに失敗しました: {e}")
        sys.exit(1)


def initialize_modules():
    """各モジュールを初期化"""
    global recorder, transcriber, summarizer

    # 出力ディレクトリを作成
    output_dir = config["output"]["directory"]
    os.makedirs(output_dir, exist_ok=True)

    # レコーダーを初期化
    recorder = AudioRecorder(
        sample_rate=config["recording"]["sample_rate"],
        channels=config["recording"]["channels"],
        output_dir=output_dir
    )

    # 文字起こしモジュールを初期化
    whisper_config = config["whisper"]
    diarization_config = config.get("diarization", {})

    transcriber = Transcriber(
        model_size=whisper_config["model_size"],
        device=whisper_config["device"],
        compute_type=whisper_config["compute_type"],
        language=whisper_config["language"],
        use_whisperx=whisper_config.get("use_whisperx", True),
        enable_diarization=diarization_config.get("enabled", True),
        min_speakers=diarization_config.get("min_speakers", 1),
        max_speakers=diarization_config.get("max_speakers", 10),
        hf_token=diarization_config.get("hf_token", None)
    )

    # 議事録生成モジュールを初期化
    summarizer = MinutesSummarizer(
        model=config["ollama"]["model"],
        base_url=config["ollama"]["base_url"]
    )

    print("すべてのモジュールを初期化しました")


# ===== Eelで公開する関数 =====

@eel.expose
def start_recording():
    """録音を開始"""
    try:
        recorder.start_recording()
        return {"success": True, "message": "録音を開始しました"}
    except Exception as e:
        print(f"録音開始エラー: {e}")
        return {"success": False, "message": str(e)}


@eel.expose
def stop_recording():
    """録音を停止"""
    try:
        file_path = recorder.stop_recording()
        return {"success": True, "message": "録音を停止しました", "file_path": file_path}
    except Exception as e:
        print(f"録音停止エラー: {e}")
        return {"success": False, "message": str(e)}


@eel.expose
def transcribe_audio(audio_file):
    """文字起こしを実行"""
    try:
        print(f"文字起こしを開始: {audio_file}")

        # 文字起こし実行
        transcript, output_file = transcriber.transcribe(
            audio_file,
            output_dir=config["output"]["directory"]
        )

        return {
            "success": True,
            "message": "文字起こしが完了しました",
            "transcript": transcript,
            "file_path": output_file
        }
    except Exception as e:
        print(f"文字起こしエラー: {e}")
        return {"success": False, "message": str(e)}


@eel.expose
def generate_minutes(transcript_text):
    """議事録を生成"""
    try:
        print("議事録を生成中...")

        # Ollamaの状態を確認
        if not summarizer.check_ollama_status():
            return {
                "success": False,
                "message": "Ollamaに接続できません。Ollamaが起動しているか確認してください。\n起動方法: ollama serve"
            }

        # 議事録生成
        minutes, output_file = summarizer.generate_minutes(
            transcript_text,
            output_dir=config["output"]["directory"]
        )

        return {
            "success": True,
            "message": "議事録の生成が完了しました",
            "minutes": minutes,
            "file_path": output_file
        }
    except Exception as e:
        print(f"議事録生成エラー: {e}")
        return {"success": False, "message": str(e)}


def main():
    """メイン関数"""
    print("=== オフライン自動議事録システム ===")
    print("Powered by Whisper (faster-whisper) + Ollama\n")

    # 設定を読み込み
    load_config()

    # モジュールを初期化
    initialize_modules()

    # 利用可能な音声デバイスを表示
    print("\n利用可能な音声デバイス:")
    AudioRecorder.list_audio_devices()

    # Ollamaの状態を確認
    print("\nOllamaの状態を確認中...")
    if summarizer.check_ollama_status():
        print("✅ Ollamaが利用可能です")
    else:
        print("⚠️  警告: Ollamaに接続できません。議事録生成を行う前に 'ollama serve' を実行してください。")

    # Eelを初期化
    print("\nWebアプリケーションを起動中...")
    eel.init("web")

    # ブラウザでアプリケーションを起動
    try:
        eel.start(
            "index.html",
            size=(900, 700),
            port=8080,
            mode="chrome",  # Chromeアプリモードで起動
            # mode="default",  # デフォルトブラウザで起動（Chromeがない場合）
        )
    except Exception as e:
        print(f"エラー: アプリケーションの起動に失敗しました: {e}")
        print("\n代替モードで起動を試みます...")
        try:
            eel.start(
                "index.html",
                size=(900, 700),
                port=8080,
                mode="default"
            )
        except Exception as e2:
            print(f"エラー: 代替モードでも起動に失敗しました: {e2}")
            sys.exit(1)


if __name__ == "__main__":
    main()
