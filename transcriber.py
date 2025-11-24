"""
文字起こしモジュール
faster-whisperを使用して音声ファイルをテキストに変換します。
"""

from faster_whisper import WhisperModel
import os
from datetime import datetime, timedelta


class Transcriber:
    """文字起こしクラス"""

    def __init__(self, model_size="large-v3", device="cpu", compute_type="int8", language="ja"):
        """
        初期化

        Args:
            model_size (str): Whisperモデルのサイズ（tiny, base, small, medium, large-v2, large-v3）
            device (str): 使用するデバイス（cpu, cuda）
            compute_type (str): 計算タイプ（int8, float16, float32）
            language (str): 言語コード（ja=日本語、en=英語など）
        """
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.language = language
        self.model = None

        print(f"Whisperモデルを初期化中: {model_size} ({device}, {compute_type})")

    def load_model(self):
        """モデルをロード"""
        if self.model is None:
            try:
                self.model = WhisperModel(
                    self.model_size,
                    device=self.device,
                    compute_type=self.compute_type
                )
                print("Whisperモデルのロードが完了しました")
            except Exception as e:
                raise RuntimeError(f"Whisperモデルのロードに失敗しました: {e}")

    def transcribe(self, audio_file, output_dir="output", progress_callback=None):
        """
        音声ファイルを文字起こし

        Args:
            audio_file (str): 音声ファイルのパス
            output_dir (str): 出力ディレクトリ
            progress_callback (callable): 進捗コールバック関数

        Returns:
            tuple: (文字起こしテキスト, 保存したファイルパス)
        """
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"音声ファイルが見つかりません: {audio_file}")

        # モデルをロード
        self.load_model()

        print(f"文字起こしを開始: {audio_file}")

        try:
            # 文字起こし実行
            segments, info = self.model.transcribe(
                audio_file,
                language=self.language,
                beam_size=5,
                vad_filter=True,  # VAD（音声区間検出）を有効化
                vad_parameters=dict(min_silence_duration_ms=500)
            )

            print(f"検出言語: {info.language} (確率: {info.language_probability:.2f})")

            # セグメントを処理
            transcript_lines = []
            full_text = []

            for segment in segments:
                # タイムスタンプを整形
                start_time = str(timedelta(seconds=int(segment.start)))
                end_time = str(timedelta(seconds=int(segment.end)))

                # タイムスタンプ付きテキスト
                line = f"[{start_time} -> {end_time}] {segment.text.strip()}"
                transcript_lines.append(line)

                # テキストのみ
                full_text.append(segment.text.strip())

                # 進捗コールバック
                if progress_callback:
                    progress_callback(segment.text.strip())

            # 文字起こし結果を結合
            transcript_with_timestamps = "\n".join(transcript_lines)
            transcript_text = "\n".join(full_text)

            # ファイルに保存
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(output_dir, f"transcript_{timestamp}.txt")

            with open(output_file, "w", encoding="utf-8") as f:
                f.write("=== 文字起こし結果（タイムスタンプ付き） ===\n\n")
                f.write(transcript_with_timestamps)
                f.write("\n\n=== 文字起こし結果（テキストのみ） ===\n\n")
                f.write(transcript_text)

            print(f"文字起こしが完了しました: {output_file}")

            return transcript_text, output_file

        except Exception as e:
            raise RuntimeError(f"文字起こしに失敗しました: {e}")

    def transcribe_realtime(self, audio_file):
        """
        音声ファイルをリアルタイムで文字起こし（ジェネレータ）

        Args:
            audio_file (str): 音声ファイルのパス

        Yields:
            dict: セグメント情報（start, end, text）
        """
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"音声ファイルが見つかりません: {audio_file}")

        # モデルをロード
        self.load_model()

        try:
            # 文字起こし実行
            segments, info = self.model.transcribe(
                audio_file,
                language=self.language,
                beam_size=5,
                vad_filter=True
            )

            for segment in segments:
                yield {
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text.strip()
                }

        except Exception as e:
            raise RuntimeError(f"リアルタイム文字起こしに失敗しました: {e}")


# テスト用コード
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("使用方法: python transcriber.py <音声ファイルパス>")
        sys.exit(1)

    audio_file = sys.argv[1]

    # 文字起こし実行
    transcriber = Transcriber(model_size="base", language="ja")  # テスト用に軽量なbaseモデルを使用

    def print_progress(text):
        print(f">> {text}")

    transcript, output_file = transcriber.transcribe(audio_file, progress_callback=print_progress)

    print("\n=== 文字起こし結果 ===")
    print(transcript)
    print(f"\n保存先: {output_file}")
