# delete_files.py
import os

def delete_files_request(file_path):
    try:
        # 删除录音文件和生成的文件
        base_path = os.path.dirname(file_path)
        base_name = os.path.basename(file_path).split('.')[0]
        files_to_delete = [
            file_path,
            os.path.join(base_path, f"{base_name}_results.html"),
            os.path.join(base_path, f"{base_name}_overlaps.html"),
            os.path.join(base_path, f"{base_name}_offoverlaps.html"),
            os.path.join(base_path, f"{base_name}_timeline.png"),
            os.path.join(base_path, f"{base_name}_allright_results.html")
        ]
        delete_files(files_to_delete)
    except Exception as e:
        print(f"Error deleting files: {e}")

def delete_files(file_paths):
    for file_path in file_paths:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted file: {file_path}")
