"""
音声録音モジュール
sounddeviceを使用してマイクから音声を録音し、WAVファイルとして保存します。
"""

import sounddevice as sd
import numpy as np
from scipy.io import wavfile
import queue
import threading
from datetime import datetime
import os


class AudioRecorder:
    """音声録音クラス"""

    def __init__(self, sample_rate=16000, channels=1, output_dir="output"):
        """
        初期化

        Args:
            sample_rate (int): サンプリングレート（Hz）
            channels (int): チャンネル数（1=モノラル、2=ステレオ）
            output_dir (str): 出力ディレクトリ
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.output_dir = output_dir
        self.is_recording = False
        self.audio_data = []
        self.audio_queue = queue.Queue()
        self.stream = None
        self.recording_thread = None

        # 出力ディレクトリの作成
        os.makedirs(output_dir, exist_ok=True)

    def _audio_callback(self, indata, frames, time, status):
        """
        音声入力コールバック関数

        Args:
            indata: 入力音声データ
            frames: フレーム数
            time: タイムスタンプ
            status: ステータス
        """
        if status:
            print(f"録音ステータス: {status}")

        if self.is_recording:
            self.audio_queue.put(indata.copy())

    def _recording_worker(self):
        """録音ワーカースレッド"""
        while self.is_recording:
            try:
                data = self.audio_queue.get(timeout=0.1)
                self.audio_data.append(data)
            except queue.Empty:
                continue

    def start_recording(self):
        """録音を開始"""
        if self.is_recording:
            raise RuntimeError("既に録音中です")

        self.is_recording = True
        self.audio_data = []

        # ストリームを開始
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            callback=self._audio_callback,
            dtype=np.int16
        )
        self.stream.start()

        # ワーカースレッドを開始
        self.recording_thread = threading.Thread(target=self._recording_worker)
        self.recording_thread.start()

        print("録音を開始しました")

    def stop_recording(self):
        """
        録音を停止してファイルに保存

        Returns:
            str: 保存したファイルのパス
        """
        if not self.is_recording:
            raise RuntimeError("録音が開始されていません")

        self.is_recording = False

        # ワーカースレッドの終了を待つ
        if self.recording_thread:
            self.recording_thread.join()

        # ストリームを停止
        if self.stream:
            self.stream.stop()
            self.stream.close()

        # 音声データを結合
        if not self.audio_data:
            raise ValueError("録音データがありません")

        audio_array = np.concatenate(self.audio_data, axis=0)

        # タイムスタンプ付きのファイル名を生成
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recording_{timestamp}.wav"
        filepath = os.path.join(self.output_dir, filename)

        # WAVファイルとして保存
        wavfile.write(filepath, self.sample_rate, audio_array)

        print(f"録音を停止しました: {filepath}")
        return filepath

    def get_recording_duration(self):
        """
        現在の録音時間を取得（秒）

        Returns:
            float: 録音時間（秒）
        """
        if not self.audio_data:
            return 0.0

        total_samples = sum(len(data) for data in self.audio_data)
        return total_samples / self.sample_rate

    @staticmethod
    def list_audio_devices():
        """利用可能な音声デバイスを一覧表示"""
        print("利用可能な音声デバイス:")
        print(sd.query_devices())

    @staticmethod
    def get_default_device():
        """デフォルトの入力デバイスを取得"""
        return sd.query_devices(kind='input')


# テスト用コード
if __name__ == "__main__":
    # デバイス一覧を表示
    AudioRecorder.list_audio_devices()

    # 録音テスト
    recorder = AudioRecorder()

    print("\n5秒間録音します...")
    recorder.start_recording()

    import time
    for i in range(5):
        time.sleep(1)
        print(f"録音中... {i+1}秒 (録音時間: {recorder.get_recording_duration():.2f}秒)")

    filepath = recorder.stop_recording()
    print(f"\n録音ファイル: {filepath}")
