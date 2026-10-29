
# app/main.py
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse

from app.pipeline import run_pipeline

app = FastAPI(title="AI Video Editing Pipeline")
PROJECTS = Path("storage/projects")


@app.post("/projects")
def create_project(
    brief: str = Form(...),
    clips: list[UploadFile] = File(...),
):
    project_id = str(uuid4())
    project_dir = PROJECTS / project_id
    source_dir = project_dir / "source"
    source_dir.mkdir(parents=True, exist_ok=True)

    allowed = {".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v"}

    try:
        for index, upload in enumerate(clips, start=1):
            suffix = Path(upload.filename or "").suffix.lower()

            if suffix not in allowed:
                raise ValueError(f"Unsupported video type: {suffix}")

            destination = source_dir / f"upload_{index:03d}{suffix}"

            with destination.open("wb") as out:
                while chunk := upload.file.read(1024 * 1024):
                    out.write(chunk)

        (project_dir / "brief.txt").write_text(
            brief, encoding="utf-8"
        )

        result = run_pipeline(project_dir, brief)

        return {
            "project_id": project_id,
            **result,
            "timeline_url": f"/projects/{project_id}/timeline",
            "edit_plan_url": f"/projects/{project_id}/edit-plan",
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Project processing failed: {exc}",
        ) from exc

    finally:
        for upload in clips:
            upload.file.close()


@app.get("/projects/{project_id}/timeline")
def download_timeline(project_id: str):
    path = PROJECTS / project_id / "timeline.otio"

    if not path.is_file():
        raise HTTPException(status_code=404, detail="Timeline not found")

    return FileResponse(
        path,
        media_type="application/octet-stream",
        filename="timeline.otio",
    )


@app.get("/projects/{project_id}/edit-plan")
def get_edit_plan(project_id: str):
    path = PROJECTS / project_id / "edit_plan.json"

    if not path.is_file():
        raise HTTPException(status_code=404, detail="Edit plan not found")

    return FileResponse(path, media_type="application/json")
