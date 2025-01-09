import os

def write_original_results_to_html(model_results, audio_file_path):
    audio_filename = os.path.basename(audio_file_path)
    output_file_path = f"./{audio_filename}_results.html"
    html_content = "<html><head><title>Model Results</title></head><body><pre style='font-family: monospace;'>"

    for result in model_results:
        segment = result[0]
        speaker = result[1]
        html_content += f"<span style='color: {speaker};'>{segment}</span><br>"

    html_content += "</pre></body></html>"

    with open(output_file_path, "w", encoding="utf-8") as output_file:
        output_file.write(html_content)

    return output_file_path
