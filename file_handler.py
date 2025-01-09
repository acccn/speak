import os
import requests
import base64

# 定义 GUI URL
gui_url = "http://localhost:5000/return_files"  # 根据需要修改为实际的 GUI URL

def handle_file(file_path):
    # 使用指定的缓存目录
    cache_dir = "/workspace/speak/cache"
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    file_info = {'file_path': file_path}
    return file_info

def save_content_to_file(content, file_path):
    with open(file_path, "w", encoding="utf-8") as output_file:
        output_file.write(content)

def return_files_to_gui(html_filepath, overlaps_filepath, offoverlaps_filepath, timeline_image_path, allright_html_filepath):
    try:
        file_contents = {
            'html_content': open(html_filepath, 'r', encoding='utf-8').read(),
            'overlaps_content': open(overlaps_filepath, 'r', encoding='utf-8').read(),
            'offoverlaps_content': open(offoverlaps_filepath, 'r', encoding='utf-8').read(),
            'timeline_image': base64.b64encode(open(timeline_image_path, 'rb').read()).decode('utf-8'),
            'allright_html_content': open(allright_html_filepath, 'r', encoding='utf-8').read()
        }

        # 回传文件内容到本地 GUI
        response = requests.post(gui_url, json=file_contents)
        if response.status_code == 200:
            print("Files successfully returned to GUI.")
            return file_contents
        else:
            print(f"Failed to return files to GUI. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error returning files: {e}")
        return None
