from flask import Flask, render_template, request, redirect, url_for
import os
import base64
import json

app = Flask(__name__)

# =========================
# Render 永続ディスク対応
# =========================
BASE_DIR = "/data"  # ← Render Disk
MEMO_FILE = os.path.join(BASE_DIR, "memos.json")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "recordings")

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# =========================
# 初期フォルダ作成
# =========================
os.makedirs(BASE_DIR, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# =========================
# メモ読み込み
# =========================
def load_memos():
    if os.path.exists(MEMO_FILE):
        try:
            with open(MEMO_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []


# =========================
# メモ保存
# =========================
def save_memos(memos):
    with open(MEMO_FILE, "w", encoding="utf-8") as f:
        json.dump(memos, f, ensure_ascii=False, indent=2)


# =========================
# トップページ
# =========================
@app.route("/", methods=["GET", "POST"])
def index():
    memos = load_memos()

    if request.method == "POST":
        memo = {
            "title": request.form.get("song_title") or "",
            "genre": request.form.get("song_genre") or "(未定)",
            "genre_sub": request.form.get("song_genre_sub") or "(未定)",
            "key": request.form.get("song_key") or "(未定)",
            "scale": request.form.get("song_scale") or "(未定)",
            "modulation": request.form.get("song_modulation") or "(未定)",
            "chord": request.form.get("song_chord") or "",
            "lyrics": request.form.get("song_lyrics") or "",
            "explanation": request.form.get("song_explanation") or "",
            "audio": request.form.get("audio_filename") or None
        }

        memos.insert(0, memo)
        save_memos(memos)

        return redirect(url_for("index"))

    return render_template("index.html", memos=memos)


# =========================
# 音声アップロード
# =========================
@app.route("/upload", methods=["POST"])
def upload():
    audio_data = request.form.get("audio_data")
    filename = request.form.get("filename")

    if not audio_data or not filename:
        return "error", 400

    filename = os.path.basename(filename)

    try:
        header, encoded = audio_data.split(",", 1)
        data = base64.b64decode(encoded)
    except:
        return "error", 400

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    with open(filepath, "wb") as f:
        f.write(data)

    return "", 200


# =========================
# 音声配信（←これ追加が重要）
# =========================
@app.route("/recordings/<filename>")
def serve_audio(filename):
    return redirect(url_for('static', filename=f'recordings/{filename}'))


# =========================
# 削除
# =========================
@app.route("/delete/<int:index>", methods=["POST"])
def delete(index):
    memos = load_memos()

    if 0 <= index < len(memos):
        memo = memos[index]

        # 音声削除
        if memo.get("audio"):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], memo["audio"])
            if os.path.exists(filepath):
                os.remove(filepath)

        memos.pop(index)
        save_memos(memos)

    return redirect(url_for("index"))


# =========================
# Render用起動設定
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)