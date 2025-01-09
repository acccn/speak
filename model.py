from pyannote.audio import Pipeline, Inference
import torch
from huggingface_hub import login

HUGGING_FACE_TOKEN = "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"
login(HUGGING_FACE_TOKEN)

pipeline = None
speaker_embedding = None

def load_model():
    global pipeline, speaker_embedding
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        use_auth_token=HUGGING_FACE_TOKEN
    )
    speaker_embedding = Inference(
        "pyannote/embedding", use_auth_token=HUGGING_FACE_TOKEN
    )
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    pipeline.to(device)
    speaker_embedding.to(device)

def run_model(file_path):
    if pipeline is None or speaker_embedding is None:
        load_model()
    diarization = pipeline(file_path)

    embeddings = {}
    speaker_ids = {}
    results = []

    for turn, _, speaker in diarization.itertracks(yield_label=True):
        if speaker not in embeddings:
            # 使用speaker_embedding生成说话人embedding
            embedding = speaker_embedding.crop(file_path, turn).data
            embedding = average_pooling(torch.tensor(embedding))
            embeddings[speaker] = embedding

        if speaker not in speaker_ids:
            # 分配唯一的说话人编号和颜色
            speaker_ids[speaker] = {
                "id": f"{len(speaker_ids) + 1:02d}",
                "color": COLORS[len(speaker_ids) % len(COLORS)]
            }

        speaker_number = speaker_ids[speaker]["id"]
        color = speaker_ids[speaker]["color"]

        original_start = turn.start
        original_end = turn.end
        converted_start = convert_time_chinese(original_start)
        converted_end = convert_time_chinese(original_end)
        float_start = convert_time_float(original_start)
        float_end = convert_time_float(original_end)
        result = f"{speaker_number}    {float_start}--{float_end}    {converted_start}--{converted_end}"
        results.append((result, color))

    return results

def convert_time_chinese(seconds):
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60
    return f"{minutes}分{remaining_seconds:.1f}秒"

def convert_time_float(seconds):
    return round(seconds, 1)

def average_pooling(embedding):
    if len(embedding.shape) == 2:
        return torch.mean(embedding, dim=0).unsqueeze(0)
    return embedding

COLORS = ["red", "blue", "green", "orange", "purple", "brown", "pink", "gray", "cyan", "magenta"]
