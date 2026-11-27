"""Integration tests for SQLiteRepository and LecMergeService against a real temporary SQLite DB."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy.orm import sessionmaker

from app.database import init_db, make_engine
from app.repository import SQLiteRepository
from app.services import LecMergeService


def _open_service(db_path: Path):
    engine = make_engine(f"sqlite:///{db_path}")
    init_db(bind=engine)
    SessionFactory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = SessionFactory()
    return engine, session, LecMergeService(SQLiteRepository(session))


def test_full_persistence_and_reopen_sqlite_database(tmp_path: Path) -> None:
    db_file = tmp_path / "persist.db"

    # Session 1: create course, lecture, ordered blocks, two fragments, and merge.
    engine1, session1, svc1 = _open_service(db_file)
    try:
        course = svc1.create_course("CSE 3206", "Software Engineering Sessional")
        lecture = svc1.create_lecture(
            course.id,
            "Lecture 4: Patterns",
            ["Composite Pattern", "Strategy Pattern"],
            lecture_date="2026-11-28",
        )
        block1_id = lecture.blocks[0].id
        block2_id = lecture.blocks[1].id

        svc1.submit_fragment(block1_id, "Amina", "F = ma")
        svc1.submit_fragment(block1_id, "Tariq", "F = m * a^2\nDetailed derivation notes.")
        merge_result = svc1.merge_block(block1_id, "most_detailed")
        assert merge_result.fragment_count == 2
        assert "Detailed derivation notes." in merge_result.merged_content
    finally:
        session1.close()
        engine1.dispose()

    # Session 2: reopen the same SQLite file from scratch to prove real persistence.
    engine2, session2, svc2 = _open_service(db_file)
    try:
        courses = svc2.list_courses()
        assert len(courses) == 1
        assert courses[0].code == "CSE 3206"

        reloaded_lecture = svc2.get_lecture(lecture.id)
        assert [b.topic for b in reloaded_lecture.blocks] == ["Composite Pattern", "Strategy Pattern"]
        assert [b.order_index for b in reloaded_lecture.blocks] == [1, 2]

        reloaded_block1 = svc2.get_block(block1_id)
        assert len(reloaded_block1.fragments) == 2
        assert [f.author_name for f in reloaded_block1.fragments] == ["Amina", "Tariq"]
        assert reloaded_block1.merged_content == "F = m * a^2\nDetailed derivation notes."

        analysis = svc2.analyze_lecture(lecture.id)
        assert analysis.covered_blocks == 1
        assert analysis.total_blocks == 2
        assert analysis.coverage_percent == 50.0
        assert analysis.blind_spot_ids == [block2_id]
        assert analysis.blocks[0].has_potential_conflict is True

        sheet = svc2.generate_study_sheet(lecture.id)
        assert "Detailed derivation notes." in sheet.markdown
        assert "Potential formula conflict — review required" in sheet.markdown
        assert "Blind spot" in sheet.markdown
    finally:
        session2.close()
        engine2.dispose()
