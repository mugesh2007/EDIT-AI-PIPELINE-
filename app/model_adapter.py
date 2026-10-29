
# app/model_adapter.py
from typing import Any


def analyze_clip(
    video_path: str,
    clip_id: str,
    brief: str,
) -> dict[str, Any]:
    """
    CONNECT THIS FUNCTION TO YOUR EXISTING MODEL.

    Return structured data, not just a paragraph.

    Expected result:
    {
        "clip_id": "clip_001",
        "duration": 45.2,
        "segments": [
            {
                "start": 0.0,
                "end": 5.0,
                "transcript": "Our product saves time.",
                "visual_summary": "Speaker explains the product.",
                "story_role": "benefit",
                "quality": 0.9
            }
        ]
    }
    """
    # Call your existing model here.
    # If your model needs frames or a transcript, extract them
    # using your existing preprocessing tools before the call.
    raise NotImplementedError("Connect your existing model")


def plan_global_edit(
    brief: str,
    all_clip_analyses: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    CONNECT THIS FUNCTION TO YOUR EXISTING MODEL.

    The model must compare segments ACROSS ALL CLIPS.

    Expected result:
    {
        "story_summary": "A concise description of the story",
        "ordered_segments": [
            {
                "clip_id": "clip_002",
                "start": 4.0,
                "end": 11.0,
                "reason": "Best introduction",
                "decision": "keep"
            }
        ],
        "review_items": []
    }
    """
    # Supply the brief + every clip's transcript and scene analysis.
    # Require strict JSON output from your model.
    raise NotImplementedError("Connect your existing model")
