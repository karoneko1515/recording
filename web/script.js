// グローバル変数
let isRecording = false;
let recordingTimer = null;
let recordingStartTime = null;
let currentAudioFile = null;
let currentTranscript = null;

// ページ読み込み時の初期化
window.onload = function() {
    console.log("アプリケーションが起動しました");
    updateStatus("待機中");
};

// ステータス更新
function updateStatus(message) {
    document.getElementById("status-text").textContent = message;
}

// 録音時間の更新
function updateRecordingTime() {
    if (!isRecording || !recordingStartTime) return;

    const elapsed = Math.floor((Date.now() - recordingStartTime) / 1000);
    const minutes = Math.floor(elapsed / 60);
    const seconds = elapsed % 60;
    const timeStr = `録音時間: ${minutes}:${seconds.toString().padStart(2, '0')}`;

    document.getElementById("recording-time").textContent = timeStr;
}

// 録音開始
async function startRecording() {
    try {
        updateStatus("録音を開始しています...");

        const result = await eel.start_recording()();

        if (result.success) {
            isRecording = true;
            recordingStartTime = Date.now();

            // ボタンの状態を更新
            document.getElementById("start-recording-btn").disabled = true;
            document.getElementById("stop-recording-btn").disabled = false;
            document.getElementById("transcribe-btn").disabled = true;
            document.getElementById("generate-minutes-btn").disabled = true;

            updateStatus("🔴 録音中...");

            // 録音時間のタイマーを開始
            recordingTimer = setInterval(updateRecordingTime, 1000);
        } else {
            updateStatus("録音の開始に失敗しました");
            alert("エラー: " + result.message);
        }
    } catch (error) {
        console.error("録音開始エラー:", error);
        updateStatus("エラーが発生しました");
        alert("録音の開始に失敗しました: " + error);
    }
}

// 録音停止
async function stopRecording() {
    try {
        updateStatus("録音を停止しています...");

        // タイマーを停止
        if (recordingTimer) {
            clearInterval(recordingTimer);
            recordingTimer = null;
        }

        const result = await eel.stop_recording()();

        if (result.success) {
            isRecording = false;
            currentAudioFile = result.file_path;

            // ボタンの状態を更新
            document.getElementById("start-recording-btn").disabled = false;
            document.getElementById("stop-recording-btn").disabled = true;
            document.getElementById("transcribe-btn").disabled = false;

            updateStatus("✅ 録音完了: " + result.file_path);
            document.getElementById("recording-time").textContent = "";

            alert("録音が完了しました!\n保存先: " + result.file_path);
        } else {
            updateStatus("録音の停止に失敗しました");
            alert("エラー: " + result.message);
        }
    } catch (error) {
        console.error("録音停止エラー:", error);
        updateStatus("エラーが発生しました");
        alert("録音の停止に失敗しました: " + error);
    }
}

// 文字起こし実行
async function transcribeAudio() {
    if (!currentAudioFile) {
        alert("録音ファイルがありません。先に録音を行ってください。");
        return;
    }

    try {
        updateStatus("文字起こし中...");
        showProgress("文字起こしを実行中です。しばらくお待ちください...", 30);

        // ボタンを無効化
        document.getElementById("transcribe-btn").disabled = true;
        document.getElementById("generate-minutes-btn").disabled = true;

        const result = await eel.transcribe_audio(currentAudioFile)();

        if (result.success) {
            currentTranscript = result.transcript;

            // 文字起こし結果を表示
            document.getElementById("transcript-text").value = result.transcript;

            // ボタンの状態を更新
            document.getElementById("generate-minutes-btn").disabled = false;

            updateStatus("✅ 文字起こし完了");
            hideProgress();

            alert("文字起こしが完了しました!\n保存先: " + result.file_path);

            // 文字起こしタブに切り替え
            showTab('transcript');
        } else {
            updateStatus("文字起こしに失敗しました");
            hideProgress();
            alert("エラー: " + result.message);

            // ボタンを再度有効化
            document.getElementById("transcribe-btn").disabled = false;
        }
    } catch (error) {
        console.error("文字起こしエラー:", error);
        updateStatus("エラーが発生しました");
        hideProgress();
        alert("文字起こしに失敗しました: " + error);

        // ボタンを再度有効化
        document.getElementById("transcribe-btn").disabled = false;
    }
}

// 議事録生成
async function generateMinutes() {
    if (!currentTranscript) {
        alert("文字起こしテキストがありません。先に文字起こしを実行してください。");
        return;
    }

    try {
        updateStatus("議事録を生成中...");
        showProgress("議事録を生成中です。しばらくお待ちください...", 60);

        // ボタンを無効化
        document.getElementById("generate-minutes-btn").disabled = true;

        const result = await eel.generate_minutes(currentTranscript)();

        if (result.success) {
            // 議事録を表示
            document.getElementById("minutes-text").value = result.minutes;

            updateStatus("✅ 議事録生成完了");
            hideProgress();

            alert("議事録の生成が完了しました!\n保存先: " + result.file_path);

            // 議事録タブに切り替え
            showTab('minutes');
        } else {
            updateStatus("議事録の生成に失敗しました");
            hideProgress();
            alert("エラー: " + result.message);
        }

        // ボタンを再度有効化
        document.getElementById("generate-minutes-btn").disabled = false;
    } catch (error) {
        console.error("議事録生成エラー:", error);
        updateStatus("エラーが発生しました");
        hideProgress();
        alert("議事録の生成に失敗しました: " + error);

        // ボタンを再度有効化
        document.getElementById("generate-minutes-btn").disabled = false;
    }
}

// タブ切り替え
function showTab(tabName) {
    // すべてのタブボタンから active クラスを削除
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(btn => btn.classList.remove('active'));

    // すべてのタブコンテンツを非表示
    const tabPanes = document.querySelectorAll('.tab-pane');
    tabPanes.forEach(pane => pane.classList.remove('active'));

    // 選択されたタブを表示
    if (tabName === 'transcript') {
        tabButtons[0].classList.add('active');
        document.getElementById('transcript-tab').classList.add('active');
    } else if (tabName === 'minutes') {
        tabButtons[1].classList.add('active');
        document.getElementById('minutes-tab').classList.add('active');
    }
}

// プログレス表示
function showProgress(message, percentage) {
    const progressSection = document.getElementById("progress-section");
    const progressText = document.getElementById("progress-text");
    const progressBarFill = document.getElementById("progress-bar-fill");

    progressText.textContent = message;
    progressBarFill.style.width = percentage + "%";
    progressSection.style.display = "block";
}

// プログレス非表示
function hideProgress() {
    const progressSection = document.getElementById("progress-section");
    progressSection.style.display = "none";
}

// 文字起こしを保存
function saveTranscript() {
    const text = document.getElementById("transcript-text").value;
    if (!text) {
        alert("文字起こしテキストがありません。");
        return;
    }

    // テキストファイルとしてダウンロード
    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'transcript_' + new Date().getTime() + '.txt';
    a.click();
    URL.revokeObjectURL(url);
}

// 議事録を保存
function saveMinutes() {
    const text = document.getElementById("minutes-text").value;
    if (!text) {
        alert("議事録がありません。");
        return;
    }

    // Markdownファイルとしてダウンロード
    const blob = new Blob([text], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'minutes_' + new Date().getTime() + '.md';
    a.click();
    URL.revokeObjectURL(url);
}

// クリップボードにコピー
function copyToClipboard(elementId) {
    const text = document.getElementById(elementId).value;
    if (!text) {
        alert("コピーするテキストがありません。");
        return;
    }

    navigator.clipboard.writeText(text).then(() => {
        alert("クリップボードにコピーしました!");
    }).catch(err => {
        console.error("コピー失敗:", err);
        alert("コピーに失敗しました。");
    });
}
