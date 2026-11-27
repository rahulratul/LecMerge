"""Repository interface and SQLite/SQLAlchemy implementation.

Keeping persistence behind ``LecMergeRepository`` lets service unit tests mock the
database boundary without opening SQLite.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import AnchorBlock, Course, Lecture, NoteFragment


class LecMergeRepository(ABC):
    """Persistence contract used by ``LecMergeService``."""

    @abstractmethod
    def list_courses(self) -> list[Course]: ...

    @abstractmethod
    def get_course(self, course_id: int) -> Course | None: ...

    @abstractmethod
    def get_course_by_code(self, code: str) -> Course | None: ...

    @abstractmethod
    def create_course(self, code: str, title: str) -> Course: ...

    @abstractmethod
    def get_lecture(self, lecture_id: int) -> Lecture | None: ...

    @abstractmethod
    def create_lecture_with_blocks(
        self,
        course_id: int,
        title: str,
        block_topics: Sequence[str],
        lecture_date: str | None = None,
    ) -> Lecture: ...

    @abstractmethod
    def get_block(self, block_id: int) -> AnchorBlock | None: ...

    @abstractmethod
    def add_fragment(self, block_id: int, author_name: str, content: str) -> NoteFragment: ...

    @abstractmethod
    def save_merged_content(self, block_id: int, merged_content: str) -> AnchorBlock | None: ...


class SQLiteRepository(LecMergeRepository):
    """SQLAlchemy-backed repository for SQLite."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def list_courses(self) -> list[Course]:
        stmt = (
            select(Course)
            .options(selectinload(Course.lectures).selectinload(Lecture.blocks).selectinload(AnchorBlock.fragments))
            .order_by(Course.code, Course.id)
        )
        return list(self._session.scalars(stmt.execution_options(populate_existing=True)).all())

    def get_course(self, course_id: int) -> Course | None:
        stmt = (
            select(Course)
            .where(Course.id == course_id)
            .options(selectinload(Course.lectures).selectinload(Lecture.blocks).selectinload(AnchorBlock.fragments))
        )
        return self._session.scalars(stmt.execution_options(populate_existing=True)).first()

    def get_course_by_code(self, code: str) -> Course | None:
        stmt = select(Course).where(Course.code == code)
        return self._session.scalars(stmt).first()

    def create_course(self, code: str, title: str) -> Course:
        course = Course(code=code, title=title)
        self._session.add(course)
        self._session.commit()
        self._session.refresh(course)
        return course

    def get_lecture(self, lecture_id: int) -> Lecture | None:
        stmt = (
            select(Lecture)
            .where(Lecture.id == lecture_id)
            .options(
                selectinload(Lecture.course),
                selectinload(Lecture.blocks).selectinload(AnchorBlock.fragments),
            )
        )
        return self._session.scalars(stmt.execution_options(populate_existing=True)).first()

    def create_lecture_with_blocks(
        self,
        course_id: int,
        title: str,
        block_topics: Sequence[str],
        lecture_date: str | None = None,
    ) -> Lecture:
        lecture = Lecture(course_id=course_id, title=title, lecture_date=lecture_date)
        for index, topic in enumerate(block_topics, start=1):
            lecture.blocks.append(AnchorBlock(order_index=index, topic=topic))
        self._session.add(lecture)
        self._session.commit()
        return self.get_lecture(lecture.id) or lecture

    def get_block(self, block_id: int) -> AnchorBlock | None:
        stmt = (
            select(AnchorBlock)
            .where(AnchorBlock.id == block_id)
            .options(
                selectinload(AnchorBlock.lecture).selectinload(Lecture.course),
                selectinload(AnchorBlock.fragments),
            )
        )
        return self._session.scalars(stmt.execution_options(populate_existing=True)).first()

    def add_fragment(self, block_id: int, author_name: str, content: str) -> NoteFragment:
        fragment = NoteFragment(block_id=block_id, author_name=author_name, content=content)
        self._session.add(fragment)
        self._session.commit()
        self._session.refresh(fragment)
        return fragment

    def save_merged_content(self, block_id: int, merged_content: str) -> AnchorBlock | None:
        block = self.get_block(block_id)
        if block is None:
            return None
        block.merged_content = merged_content
        self._session.commit()
        return self.get_block(block_id)
