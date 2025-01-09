import os
from time_axis import build_time_axis

def handle_offoverlap(timeline):
    if not timeline:
        return []

    max_time = max(end for start, end, speaker in timeline)
    time_points = [0] * int(max_time * 10 + 1)
    speakers = [None] * int(max_time * 10 + 1)

    for start, end, speaker in timeline:
        start_idx = int(start * 10)
        end_idx = int(end * 10)
        for i in range(start_idx, end_idx + 1):
            time_points[i] += 1
            speakers[i] = speaker

    non_overlaps = []
    in_non_overlap = False
    current_start, current_end = None, None
    current_speaker = None

    for i, count in enumerate(time_points):
        if count == 1:
            if not in_non_overlap:
                current_start = i / 10.0
                current_speaker = speakers[i]
                in_non_overlap = True
            elif current_speaker != speakers[i]:
                non_overlaps.append((current_speaker, current_start, current_end))
                current_start = i / 10.0
                current_speaker = speakers[i]
            current_end = i / 10.0
        else:
            if in_non_overlap:
                non_overlaps.append((current_speaker, current_start, current_end))
                in_non_overlap = False

    if in_non_overlap:
        non_overlaps.append((current_speaker, current_start, current_end))

    i = 0
    while i < len(non_overlaps) - 1:
        current_speaker, current_start, current_end = non_overlaps[i]
        next_speaker, next_start, next_end = non_overlaps[i + 1]
        if current_speaker == next_speaker and next_start - current_end < 0.5:
            non_overlaps[i] = (current_speaker, current_start, next_end)
            del non_overlaps[i + 1]
        else:
            i += 1

    final_non_overlaps = [(speaker, start, end) for speaker, start, end in non_overlaps if end - start >= 1]

    non_overlap_segments = []
    for speaker, start, end in final_non_overlaps:
        start_min = int(start // 60)
        start_sec = round(start % 60, 1)
        end_min = int(end // 60)
        end_sec = round(end % 60, 1)
        non_overlap_segments.append(f"{speaker}    {start:.1f}--{end:.1f}    {start_min}分{start_sec}秒--{end_min}分{end_sec}秒")

    return non_overlap_segments

def write_offoverlap_results_to_html(non_overlap_segments, audio_file_path):
    audio_filename = os.path.basename(audio_file_path)
    output_file_path = f"./{audio_filename}_offoverlap_results.html"
    html_content = "<html><head><title>Offoverlap Results</title></head><body><pre style='font-family: monospace;'>"

    colors = {
        "01": "red",
        "02": "blue",
        "03": "green",
        "04": "orange",
        "05": "purple"
    }

    for segment in non_overlap_segments:
        parts = segment.split(maxsplit=1)
        speaker = parts[0]
        text = parts[1] if len(parts) > 1 else ""
        color = colors.get(speaker, "black")

        text = text.replace(" ", "&nbsp;&nbsp;", 1)
        html_content += f"<span style='color: {color};'>{speaker}&nbsp;&nbsp;{text}</span><br>"

    html_content += "</pre></body></html>"

    with open(output_file_path, "w", encoding="utf-8") as output_file:
        output_file.write(html_content)

    return output_file_path

def get_offoverlap_segments(timeline):
    non_overlap_segments = handle_offoverlap(timeline)
    return non_overlap_segments
