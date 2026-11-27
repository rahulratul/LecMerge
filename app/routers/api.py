"""Versioned REST API routes (/api/v1) sharing LecMergeService with the GUI."""

from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.database import get_session
from app.repository import SQLiteRepository
from app.schemas import (
    CourseCreate,
    CourseOut,
    ErrorResponse,
    FragmentCreate,
    FragmentOut,
    LectureAnalysisOut,
    LectureCreate,
    LectureOut,
    MergeRequest,
    MergeResponse,
    StudySheetOut,
)
from app.services import LecMergeService, NotFoundError, ValidationError

router = APIRouter(prefix="/api/v1")


def get_service(session: Session = Depends(get_session)) -> LecMergeService:
    return LecMergeService(SQLiteRepository(session))


def _raise_http(exc: Exception) -> None:
    if isinstance(exc, NotFoundError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    if isinstance(exc, ValidationError):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)) from exc
    raise exc


@router.get(
    "/courses",
    response_model=list[CourseOut],
    tags=["Courses"],
    summary="List all courses",
    description="Return all stored courses ordered by course code.",
)
def list_courses(service: LecMergeService = Depends(get_service)) -> list[CourseOut]:
    return [CourseOut.model_validate(course) for course in service.list_courses()]


@router.post(
    "/courses",
    response_model=CourseOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Courses"],
    summary="Create a course",
    description="Create a new course with a unique course code and title.",
    responses={422: {"model": ErrorResponse, "description": "Validation or duplicate course code error"}},
)
def create_course(
    payload: CourseCreate,
    service: LecMergeService = Depends(get_service),
) -> CourseOut:
    try:
        course = service.create_course(code=payload.code, title=payload.title)
    except ValidationError as exc:
        _raise_http(exc)
    return CourseOut.model_validate(course)


@router.post(
    "/courses/{course_id}/lectures",
    response_model=LectureOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Lectures"],
    summary="Create a lecture with ordered anchor blocks",
    description="Create a lecture under an existing course together with its initial ordered topic blocks.",
    responses={
        404: {"model": ErrorResponse, "description": "Course not found"},
        422: {"model": ErrorResponse, "description": "Validation error"},
    },
)
def create_lecture(
    course_id: int,
    payload: LectureCreate,
    service: LecMergeService = Depends(get_service),
) -> LectureOut:
    try:
        lecture = service.create_lecture(
            course_id=course_id,
            title=payload.title,
            block_topics=payload.block_topics,
            lecture_date=payload.lecture_date,
        )
    except (NotFoundError, ValidationError) as exc:
        _raise_http(exc)
    return LectureOut.model_validate(lecture)


@router.post(
    "/blocks/{block_id}/fragments",
    response_model=FragmentOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Fragments & Merge"],
    summary="Submit a note fragment",
    description="Attach a contributor's text fragment to an anchor block without overwriting existing fragments.",
    responses={
        404: {"model": ErrorResponse, "description": "Anchor block not found"},
        422: {"model": ErrorResponse, "description": "Validation error"},
    },
)
def submit_fragment(
    block_id: int,
    payload: FragmentCreate,
    service: LecMergeService = Depends(get_service),
) -> FragmentOut:
    try:
        fragment = service.submit_fragment(
            block_id=block_id,
            author_name=payload.author_name,
            content=payload.content,
        )
    except (NotFoundError, ValidationError) as exc:
        _raise_http(exc)
    return FragmentOut.model_validate(fragment)


@router.get(
    "/lectures/{lecture_id}/analysis",
    response_model=LectureAnalysisOut,
    tags=["Analysis & Export"],
    summary="Analyze lecture coverage, blind spots, and potential conflicts",
    description="Compute coverage via the Composite hierarchy and flag potential formula conflicts per block.",
    responses={404: {"model": ErrorResponse, "description": "Lecture not found"}},
)
def analyze_lecture(
    lecture_id: int,
    service: LecMergeService = Depends(get_service),
) -> LectureAnalysisOut:
    try:
        analysis = service.analyze_lecture(lecture_id)
    except NotFoundError as exc:
        _raise_http(exc)
    return LectureAnalysisOut.model_validate(asdict(analysis))


@router.post(
    "/blocks/{block_id}/merge",
    response_model=MergeResponse,
    tags=["Fragments & Merge"],
    summary="Merge a block using a selected strategy",
    description="Select one canonical fragment using the requested strategy and persist it while keeping all fragments.",
    responses={
        404: {"model": ErrorResponse, "description": "Anchor block not found"},
        422: {"model": ErrorResponse, "description": "Block has no fragments or invalid strategy"},
    },
)
def merge_block(
    block_id: int,
    payload: MergeRequest,
    service: LecMergeService = Depends(get_service),
) -> MergeResponse:
    try:
        result = service.merge_block(block_id=block_id, strategy_key=payload.strategy)
    except (NotFoundError, ValidationError) as exc:
        _raise_http(exc)
    return MergeResponse.model_validate(asdict(result))


@router.get(
    "/lectures/{lecture_id}/study-sheet",
    response_model=StudySheetOut,
    tags=["Analysis & Export"],
    summary="Generate or download a Markdown study sheet",
    description="Compile the lecture into Markdown via StudySheetBuilder. Pass download=true to receive a .md attachment.",
    responses={404: {"model": ErrorResponse, "description": "Lecture not found"}},
)
def get_study_sheet(
    lecture_id: int,
    download: bool = Query(default=False, description="Return raw Markdown as a downloadable .md file."),
    service: LecMergeService = Depends(get_service),
):
    try:
        sheet = service.generate_study_sheet(lecture_id)
    except NotFoundError as exc:
        _raise_http(exc)

    if download:
        return Response(
            content=sheet.markdown,
            media_type="text/markdown; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="{sheet.filename}"'},
        )
    return StudySheetOut.model_validate(asdict(sheet))
