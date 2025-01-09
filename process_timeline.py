import os
from handle_offoverlap import get_offoverlap_segments
from handle_overlap import get_overlap_segments

# 颜色映射
colors = {
    "01": "red",
    "02": "blue",
    "03": "green",
    "04": "orange",
    "05": "purple",
    "N": "black"  # 固定编号N为黑色
}

def process_timeline(timeline, audio_file_path):
    # 获取 handle_offoverlap 和 handle_overlap 的结果
    offoverlap_segments = get_offoverlap_segments(timeline)
    overlap_segments = get_overlap_segments(timeline)

    # 创建时间轴
    max_time = max(end for _, end, _ in timeline)
    time_points = [0] * int(max_time * 10 + 1)
    speakers = [None] * int(max_time * 10 + 1)

    for start, end, speaker in timeline:
        start_idx = int(start * 10)
        end_idx = int(end * 10)
        for i in range(start_idx, end_idx + 1):
            time_points[i] += 1
            speakers[i] = speaker

    # 加载 offoverlap 结果到时间轴
    for segment in offoverlap_segments:
        parts = segment.split(maxsplit=1)
        speaker = parts[0]
        time_range = parts[1]
        
        # 修正time_range字符串格式
        time_range = time_range.split()[0]
        
        start, end = map(float, time_range.split('--'))
        start_idx = int(start * 10)
        end_idx = int(end * 10)
        for i in range(start_idx, end_idx + 1):
            time_points[i] += 1
            speakers[i] = speaker

    # 加载 overlap 结果到时间轴，并添加固定编号N
    for segment in overlap_segments:
        time_range = segment.split()[0]
        
        start, end = map(float, time_range.split('--'))
        start_idx = int(start * 10)
        end_idx = int(end * 10)
        for i in range(start_idx, end_idx + 1):
            time_points[i] += 1
            speakers[i] = "NN"

    # 生成新的时间段结果
    all_segments = []
    current_speaker = None
    current_start = None

    for i, count in enumerate(time_points):
        if count > 0:
            if current_speaker is None:
                current_speaker = speakers[i]
                current_start = i / 10.0
            elif current_speaker != speakers[i]:
                end_time = i / 10.0
                duration = end_time - current_start
                if duration >= 1:
                    all_segments.append({
                        "speaker": current_speaker,
                        "start": current_start,
                        "end": end_time
                    })
                current_speaker = speakers[i]
                current_start = i / 10.0
        else:
            if current_speaker is not None:
                end_time = i / 10.0
                duration = end_time - current_start
                if duration >= 1:
                    all_segments.append({
                        "speaker": current_speaker,
                        "start": current_start,
                        "end": end_time
                    })
                current_speaker = None

    if current_speaker is not None:
        end_time = len(time_points) / 10.0
        duration = end_time - current_start
        if duration >= 1:
            all_segments.append({
                "speaker": current_speaker,
                "start": current_start,
                "end": end_time
            })

    # 生成HTML文件
    audio_filename = os.path.basename(audio_file_path)
    output_file_path = f"./{audio_filename}_allright_results.html"
    html_content = "<html><head><title>Allright Results</title></head><body><pre style='font-family: monospace;'>"

    for segment in all_segments:
        speaker = segment['speaker']
        start = segment['start']
        end = segment['end']
        duration = end - start
        start_min = int(start // 60)
        start_sec = round(start % 60, 1)
        end_min = int(end // 60)
        end_sec = round(end % 60, 1)
        color = colors.get(speaker, "black")  # 默认颜色为黑色
        text = f"{speaker}&nbsp;&nbsp;{start:.1f}--{end:.1f}&nbsp;&nbsp;{duration:.1f}秒&nbsp;&nbsp;{start_min}分{start_sec}秒--{end_min}分{end_sec}秒"
        html_content += f"<span style='color: {color};'>{text}</span><br>"

    html_content += "</pre></body></html>"

    with open(output_file_path, "w", encoding="utf-8") as output_file:
        output_file.write(html_content)

    return output_file_path
