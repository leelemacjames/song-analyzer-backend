%%writefile audio_utils.py
import os
import uuid
import librosa
import numpy as np
import subprocess
from sklearn.cluster import KMeans

def download_audio(youtube_url: str, output_path: str) -> str:
    filename = f"{uuid.uuid4()}.mp3"
    filepath = os.path.join(output_path, filename)
    command = [
        "yt-dlp", "-x", "--audio-format", "mp3", "--output",
        f"{output_path}/%(id)s.%(ext)s", youtube_url
    ]
    subprocess.run(command, check=True)
    files = [f for f in os.listdir(output_path) if f.endswith(".mp3")]
    if not files:
        raise Exception("Audio download failed.")
    return os.path.join(output_path, files[0])

def analyze_youtube_audio(youtube_url: str) -> list:
    TEMP_DIR = "downloads"
    os.makedirs(TEMP_DIR, exist_ok=True)

    audio_file = download_audio(youtube_url, TEMP_DIR)

    y, sr = librosa.load(audio_file, sr=None)
    hop_length = 512
    frame_times = librosa.frames_to_time(np.arange(len(y) // hop_length), sr=sr, hop_length=hop_length)

    rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]
    times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop_length)

    X = np.array(rms).reshape(-1, 1)

    kmeans = KMeans(n_clusters=3, random_state=42).fit(X)
    labels = kmeans.labels_

    stage_mapping = {
        0: "Foundation / Build",
        1: "Climax / Shift",
        2: "Resolution / Fade"
    }

    segments = []
    prev_label = labels[0]
    start_time = times[0]

    for i in range(1, len(labels)):
        if labels[i] != prev_label:
            end_time = times[i]
            segments.append((prev_label, start_time, end_time))
            start_time = times[i]
            prev_label = labels[i]

    segments.append((prev_label, start_time, times[-1]))

    by_label = {0: [], 1: [], 2: []}
    for label, start, end in segments:
        by_label[label].append((start, end))

    final_segments = []
    for label, parts in by_label.items():
        if not parts:
            continue
        longest = max(parts, key=lambda x: x[1] - x[0])
        final_segments.append((label, *longest))

    final_segments.sort(key=lambda x: x[1])

    def format_time(seconds):
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins}:{secs:02d}"

    response = []
    for label, start, end in final_segments:
        descriptor = "Energetic & Building" if label == 0 else \
                     "Intense & Driving" if label == 1 else \
                     "Calm & Reflective"
        response.append({
            "stage_title": stage_mapping[label],
            "time_range": f"{format_time(start)} - {format_time(end)}",
            "mood_description": descriptor
        })

    os.remove(audio_file)
    return response
