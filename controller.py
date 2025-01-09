import threading
import os
from model import load_model, run_model
from file_handler import handle_file, return_files_to_gui
from original_results import write_original_results_to_html
from handle_overlap import handle_overlap, write_overlap_results_to_html
from handle_offoverlap import handle_offoverlap, write_offoverlap_results_to_html
from timeline import load_to_timeline
from plot_timeline import plot_timeline
from process_timeline import process_timeline  # 导入 process_timeline 函数

# 加载模型
model_loading_thread = threading.Thread(target=load_model)
model_loading_thread.start()

def process_file_request(file_path):
    print(f"Received file: {file_path}")  # 调试信息
    file_info = handle_file(file_path)
    model_loading_thread.join()

    model_results = run_model(file_info['file_path'])
    print(f"Model results: {model_results}")  # 调试信息

    audio_filename = os.path.basename(file_info['file_path'])
    print(f"audio_filename: {audio_filename}")  # 调试信息
    audio_filename_without_ext = os.path.splitext(audio_filename)[0]
    print(f"audio_filename_without_ext: {audio_filename_without_ext}")  # 调试信息
    timeline_image_path = os.path.join("/workspace/speak/cache", f"{audio_filename_without_ext}_timeline.png")
    print(f"timeline_image_path: {timeline_image_path}")  # 调试信息

    # 调用 original_results.py 中的函数
    html_filepath = write_original_results_to_html(model_results, file_info['file_path'])
    
    timeline_thread = threading.Thread(target=load_to_timeline, args=(model_results,))
    timeline_thread.start()
    timeline_thread.join()

    timeline = load_to_timeline(model_results)

    overlap_thread = threading.Thread(target=handle_overlap_process, args=(timeline, file_info['file_path']))
    offoverlap_thread = threading.Thread(target=handle_offoverlap_process, args=(timeline, file_info['file_path']))
    plot_thread = threading.Thread(target=plot_timeline_process, args=(timeline, timeline_image_path))
    overlap_thread.start()
    offoverlap_thread.start()
    plot_thread.start()
    overlap_thread.join()
    offoverlap_thread.join()
    plot_thread.join()

    overlaps_segments = handle_overlap(timeline)
    overlaps_filepath = write_overlap_results_to_html(overlaps_segments, file_info['file_path'])
    offoverlaps_segments = handle_offoverlap(timeline)
    offoverlaps_filepath = write_offoverlap_results_to_html(offoverlaps_segments, file_info['file_path'])

    # 调用 process_timeline 生成新的时间段结果并写入文件
    allright_html_filepath = process_timeline(timeline, file_info['file_path'])

    # 更新文件回传逻辑
    file_contents = return_files_to_gui(html_filepath, overlaps_filepath, offoverlaps_filepath, timeline_image_path, allright_html_filepath)

    if file_contents:
        print("Files successfully returned to GUI and confirmed.")
    else:
        print("Failed to return files to GUI or confirmation failed.")

    return file_contents

def handle_overlap_process(timeline, file_path):
    overlaps_segments = handle_overlap(timeline)
    overlaps_filepath = write_overlap_results_to_html(overlaps_segments, file_path)
    return overlaps_filepath

def handle_offoverlap_process(timeline, file_path):
    offoverlaps_segments = handle_offoverlap(timeline)
    offoverlaps_filepath = write_offoverlap_results_to_html(offoverlaps_segments, file_path)
    return offoverlaps_filepath

def plot_timeline_process(timeline, file_path):
    try:
        output_path = plot_timeline(timeline, file_path)
        if output_path:
            print(f"Timeline image generated successfully at: {output_path}")
        else:
            raise ValueError("Failed to generate timeline image")
    except Exception as e:
        print(f"Error generating timeline image: {e}")
