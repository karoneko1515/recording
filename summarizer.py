"""
議事録生成モジュール
Ollamaを使用して文字起こしテキストから構造化された議事録を生成します。
"""

import requests
import json
import os
from datetime import datetime


class MinutesSummarizer:
    """議事録生成クラス"""

    def __init__(self, model="llama3.1:8b", base_url="http://localhost:11434"):
        """
        初期化

        Args:
            model (str): 使用するOllamaモデル名
            base_url (str): OllamaのベースURL
        """
        self.model = model
        self.base_url = base_url
        self.api_url = f"{base_url}/api/generate"

        print(f"議事録生成システムを初期化: モデル={model}")

    def check_ollama_status(self):
        """
        Ollamaが起動しているか確認

        Returns:
            bool: Ollamaが利用可能ならTrue
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def generate_minutes(self, transcript_text, output_dir="output"):
        """
        文字起こしテキストから議事録を生成

        Args:
            transcript_text (str): 文字起こしテキスト
            output_dir (str): 出力ディレクトリ

        Returns:
            tuple: (議事録テキスト, 保存したファイルパス)
        """
        # Ollamaの状態を確認
        if not self.check_ollama_status():
            raise ConnectionError(
                "Ollamaに接続できません。Ollamaが起動しているか確認してください。\n"
                "起動方法: ollama serve"
            )

        print("議事録を生成中...")

        # プロンプトを作成
        prompt = self._create_prompt(transcript_text)

        try:
            # Ollama APIにリクエスト
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=300  # 5分タイムアウト
            )

            if response.status_code != 200:
                raise RuntimeError(f"Ollama APIエラー: {response.status_code} - {response.text}")

            result = response.json()
            minutes_text = result.get("response", "")

            if not minutes_text:
                raise ValueError("議事録の生成に失敗しました（空の応答）")

            # ファイルに保存
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(output_dir, f"minutes_{timestamp}.md")

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(minutes_text)

            print(f"議事録の生成が完了しました: {output_file}")

            return minutes_text, output_file

        except requests.exceptions.Timeout:
            raise TimeoutError("議事録の生成がタイムアウトしました（5分以上経過）")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Ollama APIへのリクエストに失敗しました: {e}")

    def generate_minutes_stream(self, transcript_text):
        """
        文字起こしテキストから議事録を生成（ストリーミング）

        Args:
            transcript_text (str): 文字起こしテキスト

        Yields:
            str: 生成された議事録の部分テキスト
        """
        # Ollamaの状態を確認
        if not self.check_ollama_status():
            raise ConnectionError(
                "Ollamaに接続できません。Ollamaが起動しているか確認してください。"
            )

        # プロンプトを作成
        prompt = self._create_prompt(transcript_text)

        try:
            # Ollama APIにストリーミングリクエスト
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": True
                },
                stream=True,
                timeout=300
            )

            if response.status_code != 200:
                raise RuntimeError(f"Ollama APIエラー: {response.status_code}")

            # ストリーミングレスポンスを処理
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        chunk = data.get("response", "")
                        if chunk:
                            yield chunk
                    except json.JSONDecodeError:
                        continue

        except requests.exceptions.Timeout:
            raise TimeoutError("議事録の生成がタイムアウトしました")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Ollama APIへのリクエストに失敗しました: {e}")

    def _create_prompt(self, transcript_text):
        """
        議事録生成用のプロンプトを作成

        Args:
            transcript_text (str): 文字起こしテキスト

        Returns:
            str: プロンプト
        """
        current_date = datetime.now().strftime("%Y年%m月%d日")

        prompt = f"""以下の会議の文字起こしから、構造化された議事録を作成してください。

# 文字起こしテキスト
{transcript_text}

# 議事録の形式
以下の形式でMarkdown形式の議事録を作成してください：

# 議事録

## 日時
{current_date}

## 参加者
（文字起こしから推測できる参加者を記載。不明な場合は「不明」と記載）

## 議題
（会議の主な議題やトピックを箇条書きで記載）

## 議論内容
（重要な議論や発言内容を要約して記載）

## 決定事項
（会議で決定された事項を箇条書きで記載）

## TODO・アクションアイテム
（今後のタスクや担当者を箇条書きで記載）

## 補足・備考
（その他の重要な情報や補足事項を記載）

---

日本語で簡潔に、かつ重要な情報を漏らさずに記載してください。
"""

        return prompt


# テスト用コード
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("使用方法: python summarizer.py <文字起こしファイルパス>")
        sys.exit(1)

    transcript_file = sys.argv[1]

    # 文字起こしテキストを読み込み
    with open(transcript_file, "r", encoding="utf-8") as f:
        transcript_text = f.read()

    # 議事録生成
    summarizer = MinutesSummarizer()

    try:
        minutes, output_file = summarizer.generate_minutes(transcript_text)
        print("\n=== 議事録 ===")
        print(minutes)
        print(f"\n保存先: {output_file}")
    except Exception as e:
        print(f"エラー: {e}")
        sys.exit(1)
