
# app/ingest.py
import json
import subprocess
from pathlib import Path


def get_duration(path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "json", str(path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return float(json.loads(result.stdout)["format"]["duration"])


def register_clips(source_dir: Path) -> list[dict]:
    clips = []

    for index, path in enumerate(sorted(source_dir.iterdir()), start=1):
        if not path.is_file():
            continue

        if path.suffix.lower() not in {
            ".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v"
        }:
            continue

        clips.append({
            "clip_id": f"clip_{index:03d}",
            "path": str(path.resolve()),
            "filename": path.name,
            "duration": get_duration(path),
        })

    if not clips:
        raise ValueError("No supported video clips were uploaded.")

    return clips
