from __future__ import annotations

from pybot.db.models import Competence, User


def _make_user() -> User:
    return User(
        first_name="Ilya",
        telegram_id=654446007,
    )


def test_add_competence_adds_single_link() -> None:
    # Given
    user = _make_user()
    python_competence = Competence(id=1, name="Python")

    # When
    user.add_competence(python_competence)

    # Then
    assert len(user.competencies) == 1
    assert user.competencies[0].competence_id == 1


def test_add_competencies_skips_duplicates() -> None:
    # Given
    user = _make_user()
    python_competence = Competence(id=1, name="Python")
    sql_competence = Competence(id=2, name="SQL")

    # When
    user.add_competencies([python_competence, python_competence, sql_competence])

    # Then
    competence_ids = sorted(link.competence_id for link in user.competencies)
    assert competence_ids == [1, 2]


def test_remove_competence_removes_single_link() -> None:
    # Given
    user = _make_user()
    python_competence = Competence(id=1, name="Python")
    sql_competence = Competence(id=2, name="SQL")
    user.add_competencies([python_competence, sql_competence])

    # When
    user.remove_competence(python_competence)

    # Then
    assert len(user.competencies) == 1
    assert user.competencies[0].competence_id == 2


def test_remove_competencies_removes_batch_and_ignores_missing() -> None:
    # Given
    user = _make_user()
    python_competence = Competence(id=1, name="Python")
    sql_competence = Competence(id=2, name="SQL")
    go_competence = Competence(id=3, name="Go")
    user.add_competencies([python_competence, sql_competence])

    # When
    user.remove_competencies([python_competence, go_competence])

    # Then
    assert len(user.competencies) == 1
    assert user.competencies[0].competence_id == 2
