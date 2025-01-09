def load_to_timeline(results):
    timeline = []
    for result in results:
        # print(f"Processing result: {result}")  # 调试打印
        result_parts = result[0].split(maxsplit=2)
        if len(result_parts) >= 2:
            speaker = result_parts[0]
            time_range = result_parts[1].split('--')
            if len(time_range) == 2:
                float_start = round(float(time_range[0]), 1)
                float_end = round(float(time_range[1]), 1)
                # print(f"Appending to timeline: start={float_start}, end={float_end}, speaker={speaker}")  # 调试打印
                timeline.append((float_start, float_end, speaker))
        else:
            print(f"Invalid result format: {result[0]}")
    timeline.sort()
    return timeline
