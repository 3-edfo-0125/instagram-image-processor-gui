import os
import re
from tkinter import messagebox
from PIL import Image, ImageFilter
import subprocess
import pyperclip
from pathlib import Path
import tkinter as tk
from tkinterdnd2 import *

# 定数
TARGET_RATIO = 1 / 1
BLUR_VALUE = 20
OUTPUT_FOLDER = Path(__file__).resolve().parent / "output"
TAG_TXT_PATH = Path(__file__).resolve().parent / "insta_tag.txt"

# 画像処理関数
def process_image(event):
    raws_paths = event.data
    if raws_paths.startswith("{") and raws_paths.endswith("}"):
        raws_paths = raws_paths[1:-1]

    matches = re.findall(r"{(.*?)}|([^ ]+)", raws_paths)
    file_paths = []
    for tup in matches:
        group1 = tup[0]
        group2 = tup[1]
        if group1:
            file_paths.append(group1)
        else:
            file_paths.append(group2)
    
    for path in file_paths:
        input_file = path
        file = os.path.basename(input_file)
        name, ext = os.path.splitext(file)
        moto_file = os.path.join(OUTPUT_FOLDER, file)

        if os.path.exists(moto_file):
            messagebox.showerror(title="エラー", message="同名ファイルがフォルダに存在しています")
            return
    
        img = Image.open(input_file)
        w, h = img.size
        current_ration = w / h

        if current_ration > TARGET_RATIO:
            new_w = int(h * TARGET_RATIO)
            left = (w - new_w) // 2
            right = left + new_w
            top = 0
            bottom = h
        else:
            new_h = int(w / TARGET_RATIO)
            top = (h - new_h) // 2
            bottom = top + new_h
            left = 0
            right = w

        cropped = img.crop((left, top, right, bottom))
        bg_img = cropped.filter(ImageFilter.GaussianBlur(BLUR_VALUE))

        bg_w, bg_h = bg_img.size
        scale = min(bg_w / w, bg_h / h)
        new_w2 = int(w * scale)
        new_h2 = int(h * scale)
        resized_img = img.resize((new_w2, new_h2), Image.LANCZOS)
    
        re_w, re_h = resized_img.size
        x = (bg_w - re_w) // 2
        y = (bg_h - re_h) // 2

        bg_img.paste(resized_img, (x,y))
    
        output_file = f'{name}_1x1{ext}'
        output_path = os.path.join(OUTPUT_FOLDER, output_file)

        img.close()
        os.rename(input_file, moto_file)
        bg_img.save(output_path)

# フォルダ開く関数
def folder_open():
    subprocess.Popen(["explorer", OUTPUT_FOLDER], shell=True)

# タグコピー関数
def tag_copy():
    with open(TAG_TXT_PATH, encoding='utf_8') as f:
        s = f.read()
        pyperclip.copy(s)

# GUI部分
root = TkinterDnD.Tk()
root.title("Instagram用画像加工")

window_width = 400
window_height = 300
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2
root.geometry(f"{window_width}x{window_height}+{x}+{y}")

root.drop_target_register(DND_FILES)
root.dnd_bind("<<Drop>>", process_image)

frame = tk.Frame(root)
frame.pack(expand=True)

label = tk.Label(frame, height=6, text="ここに画像ファイルをドラッグアンドドロップ")
button1 = tk.Button(frame, width=15, text="フォルダ表示", command=folder_open)
button2 = tk.Button(frame, width=15, text="タグコピー", command=tag_copy)

label.grid(column=0, columnspan=2, row=0)
button1.grid(column=0, row=1)
button2.grid(column=1, row=1)

root.mainloop()

