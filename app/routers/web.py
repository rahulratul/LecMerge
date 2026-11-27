"""Server-rendered GUI routes (Jinja2 + standard HTML forms)."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import quote_plus

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_session
from app.domain.conflict_detector import CONFLICT_WARNING
from app.domain.strategies import STRATEGIES
from app.repository import SQLiteRepository
from app.services import LecMergeService, NotFoundError, ValidationError

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter(include_in_schema=False)


def get_service(session: Session = Depends(get_session)) -> LecMergeService:
    return LecMergeService(SQLiteRepository(session))


def _not_found_response(request: Request, detail: str) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "404.html",
        {"detail": detail},
        status_code=404,
    )


def _redirect(url: str, message: str | None = None) -> RedirectResponse:
    target = f"{url}?message={quote_plus(message)}" if message else url
    return RedirectResponse(url=target, status_code=303)


# --- Page 1: Dashboard ---


@router.get("/", response_class=HTMLResponse)
def dashboard(
    request: Request,
    message: str | None = None,
    service: LecMergeService = Depends(get_service),
) -> HTMLResponse:
    courses = service.list_courses()
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "courses": courses,
            "message": message,
            "error": None,
            "form_code": "",
            "form_title": "",
        },
    )


@router.post("/courses", response_class=HTMLResponse)
def create_course_form(
    request: Request,
    code: str = Form(""),
    title: str = Form(""),
    service: LecMergeService = Depends(get_service),
):
    try:
        course = service.create_course(code=code, title=title)
    except ValidationError as exc:
        return templates.TemplateResponse(
            request,
            "dashboard.html",
            {
                "courses": service.list_courses(),
                "message": None,
                "error": str(exc),
                "form_code": code,
                "form_title": title,
            },
            status_code=422,
        )
    return _redirect(f"/courses/{course.id}", f"Course {course.code} created.")


# --- Page 2: Course detail ---


@router.get("/courses/{course_id}", response_class=HTMLResponse)
def course_detail(
    request: Request,
    course_id: int,
    message: str | None = None,
    service: LecMergeService = Depends(get_service),
) -> HTMLResponse:
    try:
        course = service.get_course(course_id)
        coverage = service.get_course_coverage(course_id)
    except NotFoundError as exc:
        return _not_found_response(request, str(exc))

    return templates.TemplateResponse(
        request,
        "course_detail.html",
        {
            "course": course,
            "coverage": coverage,
            "message": message,
            "error": None,
            "form_title": "",
            "form_date": "",
            "form_topics": "",
        },
    )


@router.post("/courses/{course_id}/lectures", response_class=HTMLResponse)
def create_lecture_form(
    request: Request,
    course_id: int,
    title: str = Form(""),
    lecture_date: str = Form(""),
    topics: str = Form(""),
    service: LecMergeService = Depends(get_service),
):
    try:
        block_topics = topics.splitlines()
        lecture = service.create_lecture(
            course_id=course_id,
            title=title,
            block_topics=block_topics,
            lecture_date=lecture_date,
        )
    except NotFoundError as exc:
        return _not_found_response(request, str(exc))
    except ValidationError as exc:
        course = service.get_course(course_id)
        coverage = service.get_course_coverage(course_id)
        return templates.TemplateResponse(
            request,
            "course_detail.html",
            {
                "course": course,
                "coverage": coverage,
                "message": None,
                "error": str(exc),
                "form_title": title,
                "form_date": lecture_date,
                "form_topics": topics,
            },
            status_code=422,
        )
    return _redirect(f"/lectures/{lecture.id}", f"Lecture '{lecture.title}' created.")


# --- Page 3: Lecture workspace ---


@router.get("/lectures/{lecture_id}", response_class=HTMLResponse)
def lecture_detail(
    request: Request,
    lecture_id: int,
    message: str | None = None,
    service: LecMergeService = Depends(get_service),
) -> HTMLResponse:
    try:
        lecture = service.get_lecture(lecture_id)
        analysis = service.analyze_lecture(lecture_id)
    except NotFoundError as exc:
        return _not_found_response(request, str(exc))

    return templates.TemplateResponse(
        request,
        "lecture_detail.html",
        {
            "lecture": lecture,
            "analysis": analysis,
            "conflict_warning": CONFLICT_WARNING,
            "message": message,
        },
    )


# --- Page 4: Anchor block detail ---


@router.get("/blocks/{block_id}", response_class=HTMLResponse)
def block_detail(
    request: Request,
    block_id: int,
    message: str | None = None,
    service: LecMergeService = Depends(get_service),
) -> HTMLResponse:
    try:
        block = service.get_block(block_id)
    except NotFoundError as exc:
        return _not_found_response(request, str(exc))

    analysis = service.analyze_block_entity(block)
    return templates.TemplateResponse(
        request,
        "block_detail.html",
        {
            "block": block,
            "analysis": analysis,
            "strategies": list(STRATEGIES.values()),
            "conflict_warning": CONFLICT_WARNING,
            "message": message,
            "error": None,
            "form_author": "",
            "form_content": "",
        },
    )


@router.post("/blocks/{block_id}/fragments", response_class=HTMLResponse)
def submit_fragment_form(
    request: Request,
    block_id: int,
    author_name: str = Form(""),
    content: str = Form(""),
    service: LecMergeService = Depends(get_service),
):
    try:
        service.submit_fragment(block_id=block_id, author_name=author_name, content=content)
    except NotFoundError as exc:
        return _not_found_response(request, str(exc))
    except ValidationError as exc:
        block = service.get_block(block_id)
        analysis = service.analyze_block_entity(block)
        return templates.TemplateResponse(
            request,
            "block_detail.html",
            {
                "block": block,
                "analysis": analysis,
                "strategies": list(STRATEGIES.values()),
                "conflict_warning": CONFLICT_WARNING,
                "message": None,
                "error": str(exc),
                "form_author": author_name,
                "form_content": content,
            },
            status_code=422,
        )
    return _redirect(f"/blocks/{block_id}", "Fragment submitted.")


@router.post("/blocks/{block_id}/merge", response_class=HTMLResponse)
def merge_block_form(
    request: Request,
    block_id: int,
    strategy: str = Form("most_detailed"),
    service: LecMergeService = Depends(get_service),
):
    try:
        result = service.merge_block(block_id=block_id, strategy_key=strategy)
    except NotFoundError as exc:
        return _not_found_response(request, str(exc))
    except ValidationError as exc:
        block = service.get_block(block_id)
        analysis = service.analyze_block_entity(block)
        return templates.TemplateResponse(
            request,
            "block_detail.html",
            {
                "block": block,
                "analysis": analysis,
                "strategies": list(STRATEGIES.values()),
                "conflict_warning": CONFLICT_WARNING,
                "message": None,
                "error": str(exc),
                "form_author": "",
                "form_content": "",
            },
            status_code=422,
        )
    return _redirect(
        f"/blocks/{block_id}",
        f"Canonical selection saved using '{result.strategy_label}' (fragment #{result.selected_fragment_id} by {result.selected_author}).",
    )


# --- Page 5: Study sheet ---


@router.get("/lectures/{lecture_id}/study-sheet", response_class=HTMLResponse)
def study_sheet_page(
    request: Request,
    lecture_id: int,
    service: LecMergeService = Depends(get_service),
) -> HTMLResponse:
    try:
        sheet = service.generate_study_sheet(lecture_id)
    except NotFoundError as exc:
        return _not_found_response(request, str(exc))

    return templates.TemplateResponse(
        request,
        "study_sheet.html",
        {"sheet": sheet},
    )


@router.get("/lectures/{lecture_id}/study-sheet/download")
def download_study_sheet(
    request: Request,
    lecture_id: int,
    service: LecMergeService = Depends(get_service),
) -> Response:
    try:
        sheet = service.generate_study_sheet(lecture_id)
    except NotFoundError as exc:
        return _not_found_response(request, str(exc))

    return Response(
        content=sheet.markdown,
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{sheet.filename}"'},
    )
