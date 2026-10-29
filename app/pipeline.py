
# app/pipeline.py
import json
from pathlib import Path

from app.ingest import register_clips
from app.model_adapter import analyze_clip, plan_global_edit
from app.export_otio import export_timeline


def save_json(path: Path, data: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def run_pipeline(project_dir: Path, brief: str) -> dict:
    source_dir = project_dir / "source"
    analysis_dir = project_dir / "analysis"
    analysis_dir.mkdir(parents=True, exist_ok=True)

    # A. Register original uploaded media.
    clips = register_clips(source_dir)
    save_json(project_dir / "media_manifest.json", clips)

    # B. Understand each clip separately.
    analyses = []

    for clip in clips:
        result = analyze_clip(
            video_path=clip["path"],
            clip_id=clip["clip_id"],
            brief=brief,
        )

        # Keep the real source metadata authoritative.
        result["clip_id"] = clip["clip_id"]
        result["duration"] = clip["duration"]

        save_json(
            analysis_dir / f'{clip["clip_id"]}.json',
            result,
        )
        analyses.append(result)

    # C. Create one global story/edit plan from ALL clips.
    context = {
        "brief": brief,
        "clips": analyses,
    }
    save_json(project_dir / "story_context.json", context)

    plan = plan_global_edit(brief, analyses)

    if not isinstance(plan.get("ordered_segments"), list):
        raise ValueError("Model did not return ordered_segments.")

    # D. Validate source IDs and time ranges before export.
    by_id = {c["clip_id"]: c for c in clips}
    accepted = []
    review = list(plan.get("review_items", []))

    for item in plan["ordered_segments"]:
        if item.get("decision") != "keep":
            continue

        clip = by_id.get(item.get("clip_id"))
        if clip is None:
            review.append({
                "item": item,
                "reason": "Unknown source clip ID",
            })
            continue

        try:
            start = float(item["start"])
            end = float(item["end"])
        except (KeyError, TypeError, ValueError):
            review.append({
                "item": item,
                "reason": "Missing or invalid timestamps",
            })
            continue

        if start < 0 or end <= start or end > clip["duration"] + 0.05:
            review.append({
                "item": item,
                "reason": "Invalid source time range",
            })
            continue

        accepted.append({
            **item,
            "start": start,
            "end": min(end, clip["duration"]),
        })

    plan["ordered_segments"] = accepted
    plan["review_items"] = review

    if not accepted:
        raise ValueError("No valid segments to export.")

    save_json(project_dir / "edit_plan.json", plan)

    # E. Generate an editable timeline; do not render a flattened video.
    timeline_path = project_dir / "timeline.otio"
    export_timeline(clips, plan, timeline_path)

    return {
        "status": "completed",
        "timeline": str(timeline_path),
        "selected_segments": len(accepted),
        "review_items": len(review),
        "story_summary": plan.get("story_summary", ""),
    }
