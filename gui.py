import os
import tkinter as tk
from tkinter import filedialog, scrolledtext
import threading
import requests
import pygame
import time
import base64

# 初始化 pygame
pygame.mixer.init()

# 服务器 URL
SERVER_URL = "https://7d9a-134-175-200-39.ngrok-free.app"
DELETE_URL = f"{SERVER_URL}/delete_files"

def play_sound():
    base_path = os.path.abspath(".")
    sound_file = os.path.join(base_path, "bell.mp3")
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.play(loops=-1)
    threading.Timer(2, stop_sound).start()  # 30 秒后自动停止铃声
    stop_sound_event.wait()
    pygame.mixer.music.stop()

def stop_sound():
    stop_sound_event.set()

def select_file():
    file_path = filedialog.askopenfilename(
        title="选择音频文件",
        filetypes=[("音频文件", "*.wav")]
    )
    if file_path:
        result_text.delete(1.0, tk.END)
        stop_sound_event.clear()
        threading.Thread(target=process_audio,
                         args=(file_path, result_text, stop_sound_event, play_sound, time_label)).start()

def process_audio(file_path, result_text, stop_sound_event, play_sound, time_label):
    start_time = time.time()  # 记录开始时间
    url = f"{SERVER_URL}/process_audio"
    files = {'file': open(file_path, 'rb')}
    print(f"Uploading file to {url}")  # 调试信息
    response = requests.post(url, files=files)

    print(f"Response status code: {response.status_code}")  # 调试信息
    if response.status_code == 200:
        data = response.json()
        save_received_files(data, file_path)
        result_text.insert(tk.END, f"文件: {os.path.basename(file_path)} - 回传成功\n")
        end_time = time.time()  # 记录结束时间
        total_time = end_time - start_time
        time_label.config(text=f"处理时间: {total_time:.2f} 秒")
        play_sound()
    else:
        result_text.insert(tk.END, f"请求失败，状态码: {response.status_code}\n")
        print(f"请求失败，状态码: {response.status_code}")  # 调试信息

def save_received_files(data, original_file_path):
    if data is None:
        raise ValueError("Received data is None")
    if 'html_content' not in data or 'overlaps_content' not in data or 'offoverlaps_content' not in data or 'timeline_image' not in data or 'allright_html_content' not in data:
        raise KeyError("Missing expected keys in received data")

    original_dir = os.path.dirname(original_file_path)
    base_name = os.path.basename(original_file_path).split('.')[0]

    # 保存 HTML 文件
    with open(os.path.join(original_dir, f"{base_name}_results.html"), 'w', encoding='utf-8') as file:
        file.write(data['html_content'])
    with open(os.path.join(original_dir, f"{base_name}_overlaps.html"), 'w', encoding='utf-8') as file:
        file.write(data['overlaps_content'])
    with open(os.path.join(original_dir, f"{base_name}_offoverlaps.html"), 'w', encoding='utf-8') as file:
        file.write(data['offoverlaps_content'])
    with open(os.path.join(original_dir, f"{base_name}_allright_results.html"), 'w', encoding='utf-8') as file:
        file.write(data['allright_html_content'])

    # 保存 PNG 文件
    with open(os.path.join(original_dir, f"{base_name}_timeline.png"), 'wb') as file:
        file.write(base64.b64decode(data['timeline_image']))

    result_text.insert(tk.END, f"文件已保存: {base_name}_results.html\n")
    result_text.insert(tk.END, f"文件已保存: {base_name}_overlaps.html\n")
    result_text.insert(tk.END, f"文件已保存: {base_name}_offoverlaps.html\n")
    result_text.insert(tk.END, f"文件已保存: {base_name}_allright_results.html\n")
    result_text.insert(tk.END, f"文件已保存: {base_name}_timeline.png\n")

    # 向 server 发送删除文件请求
    print(f"Sending delete request for: {original_file_path}")  # 调试信息
    delete_response = requests.post(DELETE_URL, json={"file_path": original_file_path})
    print(f"Delete response status code: {delete_response.status_code}")  # 调试信息
    if delete_response.status_code == 200:
        result_text.insert(tk.END, "文件已成功删除。\n")
    else:
        result_text.insert(tk.END, f"删除文件失败，状态码: {delete_response.status_code}\n")

def toggle_always_on_top():
    global is_on_top
    is_on_top = not is_on_top
    root.attributes("-topmost", is_on_top)

root = tk.Tk()
root.title("音频处理器 - 说话人分离和验证")

is_on_top = False
stop_sound_event = threading.Event()

button_frame = tk.Frame(root)
button_frame.pack(pady=10)

select_button = tk.Button(button_frame, text="选择音频文件并处理", command=select_file)
select_button.grid(row=0, column=0, padx=5)

top_button = tk.Button(button_frame, text="置顶窗口", command=toggle_always_on_top)
top_button.grid(row=0, column=1, padx=5)

stop_button = tk.Button(button_frame, text="停止提示音", command=stop_sound)
stop_button.grid(row=0, column=2, padx=5)

result_frame = tk.Frame(root)
result_frame.pack(pady=20)

result_text = scrolledtext.ScrolledText(result_frame, width=80, height=20, font=("Arial", 10))
result_text.pack(side=tk.LEFT)

time_label = tk.Label(root, text="处理时间: ")
time_label.pack(pady=10)

root.mainloop()
