"""
文字起こしモジュール
faster-whisper または WhisperX を使用して音声ファイルをテキストに変換します。
WhisperXを使用する場合、話者識別機能も利用できます。
"""

import os
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)


class Transcriber:
    """文字起こしクラス"""

    def __init__(
        self,
        model_size="large-v3",
        device="cpu",
        compute_type="int8",
        language="ja",
        use_whisperx=True,
        enable_diarization=True,
        min_speakers=1,
        max_speakers=10,
        hf_token=None
    ):
        """
        初期化

        Args:
            model_size (str): Whisperモデルのサイズ（tiny, base, small, medium, large-v2, large-v3）
            device (str): 使用するデバイス（cpu, cuda）
            compute_type (str): 計算タイプ（int8, float16, float32）
            language (str): 言語コード（ja=日本語、en=英語など）
            use_whisperx (bool): WhisperXを使用するか（話者識別機能を含む）
            enable_diarization (bool): 話者識別を有効にするか
            min_speakers (int): 最小話者数
            max_speakers (int): 最大話者数
            hf_token (str): Hugging Face Token（話者識別に必要）
        """
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.language = language
        self.use_whisperx = use_whisperx
        self.enable_diarization = enable_diarization and use_whisperx
        self.min_speakers = min_speakers
        self.max_speakers = max_speakers
        self.hf_token = hf_token
        self.model = None

        mode = "WhisperX" if use_whisperx else "faster-whisper"
        diar_status = "(話者識別あり)" if self.enable_diarization else ""
        print(f"Whisperモデルを初期化中: {mode} - {model_size} ({device}, {compute_type}) {diar_status}")

    def load_model(self):
        """モデルをロード"""
        if self.model is not None:
            return

        try:
            if self.use_whisperx:
                # WhisperXを使用
                import whisperx
                print("WhisperXモデルをロード中...")
                self.model = whisperx.load_model(
                    self.model_size,
                    device=self.device,
                    compute_type=self.compute_type,
                    language=self.language
                )
                print("WhisperXモデルのロードが完了しました")
            else:
                # faster-whisperを使用
                from faster_whisper import WhisperModel
                print("faster-whisperモデルをロード中...")
                self.model = WhisperModel(
                    self.model_size,
                    device=self.device,
                    compute_type=self.compute_type
                )
                print("faster-whisperモデルのロードが完了しました")

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
            if self.use_whisperx:
                return self._transcribe_whisperx(audio_file, output_dir, progress_callback)
            else:
                return self._transcribe_faster_whisper(audio_file, output_dir, progress_callback)

        except Exception as e:
            raise RuntimeError(f"文字起こしに失敗しました: {e}")

    def _transcribe_whisperx(self, audio_file, output_dir, progress_callback):
        """WhisperXで文字起こし（話者識別付き）"""
        import whisperx
        import torch

        # Step 1: 文字起こし
        print("Step 1/4: 文字起こし中...")
        audio = whisperx.load_audio(audio_file)
        result = self.model.transcribe(audio, batch_size=16)

        # Step 2: アライメント（タイムスタンプの精度向上）
        print("Step 2/4: タイムスタンプの調整中...")
        model_a, metadata = whisperx.load_align_model(
            language_code=self.language,
            device=self.device
        )
        # whisperx.align()の戻り値でresult全体を置き換える
        result = whisperx.align(
            result["segments"],
            model_a,
            metadata,
            audio,
            self.device,
            return_char_alignments=False
        )

        # Step 3: 話者識別
        diarize_result = None
        if self.enable_diarization:
            if not self.hf_token:
                print("警告: Hugging Face Tokenが設定されていません。話者識別をスキップします。")
            else:
                try:
                    print("Step 3/4: 話者識別中...")
                    # pyannote.audioから直接Pipelineをインポート
                    from pyannote.audio import Pipeline

                    diarize_model = Pipeline.from_pretrained(
                        "pyannote/speaker-diarization-3.1",
                        use_auth_token=self.hf_token
                    )

                    # デバイスを設定
                    if self.device == "cuda":
                        diarize_model.to(torch.device("cuda"))

                    diarize_result = diarize_model(
                        audio_file,  # ← ファイルパスを渡す（audioではなく）
                        min_speakers=self.min_speakers,
                        max_speakers=self.max_speakers
                    )
                    result = whisperx.assign_word_speakers(diarize_result, result)
                    print("話者識別が完了しました")
                except Exception as e:
                    import traceback
                    print(f"警告: 話者識別に失敗しました:")
                    print(f"エラー詳細: {type(e).__name__}: {str(e)}")
                    print(f"トレースバック:")
                    traceback.print_exc()
                    print("話者識別なしで続行します。")

        # Step 4: 結果の整形
        print("Step 4/4: 結果を整形中...")
        transcript_lines = []
        full_text = []

        for segment in result["segments"]:
            start_time = str(timedelta(seconds=int(segment["start"])))
            end_time = str(timedelta(seconds=int(segment["end"])))
            text = segment["text"].strip()

            # 話者情報を取得
            speaker = segment.get("speaker", None)
            if speaker:
                line = f"[{start_time} -> {end_time}] {speaker}: {text}"
            else:
                line = f"[{start_time} -> {end_time}] {text}"

            transcript_lines.append(line)
            full_text.append(text)

            # 進捗コールバック
            if progress_callback:
                progress_callback(text)

        # 文字起こし結果を結合
        transcript_with_timestamps = "\n".join(transcript_lines)
        transcript_text = "\n".join(full_text)

        # ファイルに保存
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f"transcript_{timestamp}.txt")

        with open(output_file, "w", encoding="utf-8") as f:
            title = "話者識別付き" if self.enable_diarization and diarize_result else "タイムスタンプ付き"
            f.write(f"=== 文字起こし結果（{title}） ===\n\n")
            f.write(transcript_with_timestamps)
            f.write("\n\n=== 文字起こし結果（テキストのみ） ===\n\n")
            f.write(transcript_text)

        # メモリ解放
        del model_a
        if self.device == "cuda":
            torch.cuda.empty_cache()

        print(f"文字起こしが完了しました: {output_file}")
        return transcript_text, output_file

    def _transcribe_faster_whisper(self, audio_file, output_dir, progress_callback):
        """faster-whisperで文字起こし"""
        # 文字起こし実行
        segments, info = self.model.transcribe(
            audio_file,
            language=self.language,
            beam_size=5,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500)
        )

        print(f"検出言語: {info.language} (確率: {info.language_probability:.2f})")

        # セグメントを処理
        transcript_lines = []
        full_text = []

        for segment in segments:
            start_time = str(timedelta(seconds=int(segment.start)))
            end_time = str(timedelta(seconds=int(segment.end)))
            text = segment.text.strip()

            line = f"[{start_time} -> {end_time}] {text}"
            transcript_lines.append(line)
            full_text.append(text)

            # 進捗コールバック
            if progress_callback:
                progress_callback(text)

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


# テスト用コード
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("使用方法: python transcriber.py <音声ファイルパス> [--no-diarization]")
        sys.exit(1)

    audio_file = sys.argv[1]
    enable_diarization = "--no-diarization" not in sys.argv

    # 文字起こし実行
    transcriber = Transcriber(
        model_size="base",
        language="ja",
        use_whisperx=True,
        enable_diarization=enable_diarization
    )

    def print_progress(text):
        print(f">> {text}")

    transcript, output_file = transcriber.transcribe(audio_file, progress_callback=print_progress)

    print("\n=== 文字起こし結果 ===")
    print(transcript)
    print(f"\n保存先: {output_file}")
