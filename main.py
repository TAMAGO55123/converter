import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import tempfile
import subprocess
import pathlib
import re
import shutil
import atexit
import sys

CREATE_NO_WINDOW = 0x08000000

p:subprocess.Popen = None
movie_path:pathlib.Path = None

temp_dir = tempfile.mkdtemp(prefix="converterv_")
temp_path = pathlib.Path(temp_dir)
print(temp_dir)

def get_base_path():
    if getattr(sys, 'frozen', False):
        # PyInstallerでEXE化されて動いている場合 (conv.exeのあるフォルダ)
        return pathlib.Path(sys.executable).parent
    # 通常の.pyスクリプトとして動いている場合
    return pathlib.Path(__file__).parent

root = tk.Tk()
root.title("Converter-V")
root.resizable(True, True)
root.geometry("500x500")
root.iconbitmap(str(get_base_path() / "ico.ico"))

def log_write(log, line: str):
    log.config(state="normal")

    line = line.rstrip("\n")
    log.insert("end", line + "\n")

    log.see("end")
    log.config(state="disabled")

# ダウンローダー

yt = tk.LabelFrame(
    root,
    text="動画・音声 ダウンロード"
)
yt.pack()

url_frame = tk.Frame(yt)
url_frame.pack(anchor="w", pady=4)

url_label = tk.Label(
    url_frame,
    text="URL:"
)
url_label.pack(side="left")

url = tk.Entry(
    url_frame,
    width=30
)
url.pack(side="left")

ext_frame = tk.Frame(yt)
ext_frame.pack(anchor="w", pady=4)

ext_label = tk.Label(
    ext_frame,
    text="タイプ:"
)
ext_label.pack(side="left")

dlp_file_ext = ttk.Combobox(
    ext_frame,
    values=[
        "MP4",
        "MP3",
        "WAV(PCM)",
    ],
    state="readonly"
)
dlp_file_ext.current(0)
dlp_file_ext.pack(pady=10, side="left")

dlp_log = tk.Text(yt,height=10,state="disabled")

# ★ ユーザー指定のパス構造に合わせて修正
def get_ffmpeg_path():
    return get_base_path() / "ffmpeg" / "bin" / "ffmpeg.exe"

# ★ ルート直下から取得するように修正
def get_yt_dlp_path():
    return get_base_path() / "yt-dlp.exe"

def download_button():
    global p
    d_url = url.get()
    if d_url:
        p = subprocess.Popen(
            [str(get_yt_dlp_path()), "-t", "mp4", d_url],
            creationflags=CREATE_NO_WINDOW,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=False,
            cwd=temp_dir
        )
        
        dlp_log_output()
    else:
        messagebox.showerror(
            title="動画・音声ダウンロード",
            message="URLが入力されていません"
        )

def dlp_log_output():
    global p, movie_path
    line = p.stdout.readline()
    line = line.decode("utf-8", errors="replace")
    
    if line:
        log_write(dlp_log, line)
        
    if p.poll() is None:
        root.after(50, dlp_log_output)
    else:
        # yt-dlpのプロセスが完全に終了した時の処理
        # ★ .mp4 固定なので、直接 glob で取得するように簡略化
        media_files = list(temp_path.glob("*.mp4"))
        
        # 安全対策：ファイルがうまく取得できなかった場合のエラー落ちを防ぐ
        if not media_files:
            log_write(dlp_log, "エラー: ダウンロードされたMP4ファイルが見つかりません。")
            return
            
        movie_path = media_files[0]
        
        if movie_path:
            category = dlp_file_ext.get()
            if category == "MP4":
                filename = filedialog.asksaveasfilename(
                    initialfile=movie_path.name,
                    filetypes=[("MP4", ".mp4")]
                )
                if not filename:
                    movie_path.unlink()
                    log_write(dlp_log, "保存先が選択されませんでした。")
                    return
                dst = pathlib.Path(filename)
                shutil.copy2(movie_path, dst)
                movie_path.unlink()
                log_write(dlp_log, "保存が完了しました。")
                
            if category == "MP3":
                filename = filedialog.asksaveasfilename(
                    initialfile=f"{movie_path.stem}.mp3",
                    filetypes=[("MP3", ".mp3")]
                )
                if not filename:
                    movie_path.unlink()
                    log_write(dlp_log, "保存先が選択されませんでした。")
                    return
                dst = pathlib.Path(filename)
                p = subprocess.Popen(
                    [str(get_ffmpeg_path()), "-i", str(movie_path.resolve()), "-ab", "128", str(dst.resolve())],
                    creationflags=CREATE_NO_WINDOW,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=False,
                    cwd=str(dst.parent)
                )
                root.after(50, dlp_change)
                
            if category == "WAV(PCM)":
                filename = filedialog.asksaveasfilename(
                    initialfile=f"{movie_path.stem}.wav",
                    filetypes=[("WAV", ".wav")]
                )
                if not filename:
                    movie_path.unlink()
                    log_write(dlp_log, "保存先が選択されませんでした。")
                    return
                dst = pathlib.Path(filename)
                p = subprocess.Popen(
                    [str(get_ffmpeg_path()), "-i", str(movie_path.resolve()), "-acodec", "pcm_s16le", str(dst.resolve())],
                    creationflags=CREATE_NO_WINDOW,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=False,
                    cwd=str(dst.parent)
                )
                root.after(50, dlp_change)

def dlp_change():
    global p, movie_path
    if p is None:
        return
    line = p.stdout.readline()
    line = line.decode("utf-8", errors="replace")
    if line:
        log_write(dlp_log, line)

    if p.poll() is None:
        root.after(50, dlp_change)
    else:
        movie_path.unlink()
        log_write(dlp_log, "保存が完了しました。")
    
dlp_sub_frame = tk.Frame(yt)
dlp_sub_frame.pack(anchor="w", pady=4)

dlp_submit = tk.Button(
    dlp_sub_frame,
    text="ダウンロード",
    command=download_button
)
dlp_submit.pack(side="left",pady=4)
dlp_log.pack(side="left")

# WAVE変換

pcm = tk.LabelFrame(
    root,
    text="Wav(PCM)変換"
)
pcm.pack()

def change_pcm():
    global p
    before = filedialog.askopenfilename(
        filetypes=[
            ("Media", "*.mp4 *.mkv *.mov *.avi *.flv *.ts *.m2ts *.mpg *.mpeg *.webm *.wav *.mp3 *.ogg *.m4a *.aac *.flac"),
            ("MP4", "*.mp4"),
            ("MKV", "*.mkv"),
            ("MOV", "*.mov"),
            ("AVI", "*.avi"),
            ("FLV", "*.flv"),
            ("TS", "*.ts *.m2ts"),
            ("Audio", "*.wav *.mp3 *.ogg *.m4a *.aac *.flac"),
            ("All files", "*.*")
        ]
    )

    if not before:
        log_write(pcm_log, "読み込み先が選択されませんでした。")
        return
    bef_path = pathlib.Path(before)
    after = filedialog.asksaveasfilename(
        filetypes=[
            ("WAV", ".wav")
        ],
        initialfile=f"{bef_path.stem}.wav"
    )
    if not after:
        log_write(pcm_log, "保存先が選択されませんでした。")
        return
    aft_path = pathlib.Path(after)
    

    p = subprocess.Popen(
        [str(get_ffmpeg_path()), "-i", str(bef_path.resolve()), "-acodec", "pcm_s16le", str(aft_path.resolve())],
        creationflags=CREATE_NO_WINDOW,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=False
    )
    root.after(50, pcm_change)

def pcm_change():
    global p
    if p is None:
        return
    line = p.stdout.readline()
    line = line.decode("utf-8", errors="replace")
    if line:
        log_write(pcm_log, line)
    if p.poll() is None:
        root.after(50, pcm_change)
    else:
        log_write(pcm_log, "保存が完了しました。")


pcm_btn = tk.Button(
    pcm,
    text="読み込み",
    command=change_pcm
)
pcm_btn.pack()

pcm_log = tk.Text(pcm, height=10)
pcm_log.pack()

# Temp削除処理

def cleanup_tempdir():
    try:
        if p and p.poll() is None:
            p.kill()
    except Exception:
        pass
    if temp_dir and temp_path.exists():
        shutil.rmtree(temp_dir)

atexit.register(cleanup_tempdir)

def on_close():
    cleanup_tempdir()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)

try:
    root.mainloop()
except KeyboardInterrupt:
    cleanup_tempdir()
    raise