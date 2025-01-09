from flask import Flask, request, jsonify
import os
import base64  # 添加 base64 导入
from controller import process_file_request
from delete_files import delete_files_request  # 从 delete_files 导入

app = Flask(__name__)

@app.route('/process_audio', methods=['POST'])
def process_audio():
    file = request.files['file']
    filename = file.filename
    file_path = os.path.join('/workspace/speak/cache', filename)
    file.save(file_path)

    response = process_file_request(file_path)
    return jsonify(response)

@app.route('/return_files', methods=['POST'])
def return_files():
    try:
        file_contents = request.get_json()
        if file_contents is None:
            raise ValueError("No data received from request")

        # 获取文件内容
        html_content = file_contents.get('html_content')
        overlaps_content = file_contents.get('overlaps_content')
        offoverlaps_content = file_contents.get('offoverlaps_content')
        timeline_image = file_contents.get('timeline_image')
        allright_html_content = file_contents.get('allright_html_content')

        if not html_content or not overlaps_content or not offoverlaps_content or not timeline_image or not allright_html_content:
            raise KeyError("Missing expected keys in received data")

        return jsonify({"message": "Files successfully received"}), 200
    except Exception as e:
        print(f"Error in return_files: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/delete_files', methods=['POST'])
def delete_files():
    data = request.get_json()
    file_path = data.get('file_path')
    if file_path:
        delete_files_request(file_path)
        return jsonify({"message": "Files successfully deleted"}), 200
    else:
        return jsonify({"error": "No file path provided"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
