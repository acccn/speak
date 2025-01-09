import os
from time_axis import build_time_axis

def handle_overlap(timeline):
    if not timeline:
        return []

    # 获取时间轴的最大时间
    max_time = max(end for _, end, _ in timeline)

    # 创建一个包含音频总长度所有时间点的时间轴
    time_points = [0] * int(max_time * 10 + 1)

    # 标记每个时间段的起始和结束
    for start, end, _ in timeline:
        start_idx = int(start * 10)
        end_idx = int(end * 10)
        for i in range(start_idx, end_idx + 1):
            time_points[i] += 1

    # 分析重叠的区间
    overlaps = []
    in_overlap = False
    current_start, current_end = None, None

    for i, count in enumerate(time_points):
        if count > 1:
            if not in_overlap:
                current_start = i / 10.0
                in_overlap = True
            current_end = i / 10.0
        else:
            if in_overlap:
                overlaps.append((current_start, current_end))
                in_overlap = False

    # 添加最后一个重叠区间
    if in_overlap:
        overlaps.append((current_start, current_end))

    # 规则一：合并距离小于0.5秒的段落
    merged_overlaps = []
    current_start, current_end = None, None
    for start, end in overlaps:
        if current_start is None:
            current_start, current_end = start, end
        else:
            if start - current_end < 0.5:
                current_end = max(current_end, end)
            else:
                merged_overlaps.append((current_start, current_end))
                current_start, current_end = start, end
    if current_start is not None:
        merged_overlaps.append((current_start, current_end))

    # 规则二：删除小于0.5秒的段落
    final_overlaps = [(start, end) for start, end in merged_overlaps if end - start >= 1]

    # 格式化输出，参考 original_results.py
    overlap_segments = []
    for start, end in final_overlaps:
        start_min = int(start // 60)
        start_sec = round(start % 60, 1)
        end_min = int(end // 60)
        end_sec = round(end % 60, 1)
        overlap_segments.append(f"{start:.1f}--{end:.1f}    {start_min}分{start_sec}秒--{end_min}分{end_sec}秒")

    return overlap_segments

def write_overlap_results_to_html(overlap_segments, audio_file_path):
    audio_filename = os.path.basename(audio_file_path)
    output_file_path = f"./{audio_filename}_overlap_results.html"
    html_content = "<html><head><title>Overlap Results</title></head><body><pre style='font-family: monospace;'>"

    for segment in overlap_segments:
        html_content += f"{segment}<br>"

    html_content += "</pre></body></html>"

    with open(output_file_path, "w", encoding="utf-8") as output_file:
        output_file.write(html_content)

    return output_file_path

def get_overlap_segments(timeline):
    overlap_segments = handle_overlap(timeline)
    return overlap_segments
