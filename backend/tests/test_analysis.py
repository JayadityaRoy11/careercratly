from app.services.ats_analyzer import analyze_resume_against_role
from app.services.skill_extractor import SpacyPhraseMatcherExtractor
from tests.conftest import SAMPLE_SKILLS, make_resume_docx


def test_skill_extraction():
    extractor = SpacyPhraseMatcherExtractor()
    skills = extractor.extract(
        "Worked with Python, Postgres, sklearn, JS, FastAPI, Docker, and REST APIs."
    )
    assert "Python" in skills
    assert "PostgreSQL" in skills
    assert "scikit-learn" in skills
    assert "JavaScript" in skills
    assert "FastAPI" in skills


def test_ats_scoring_is_deterministic():
    text = (
        "Education B.Tech. Experience intern. Projects built APIs. Skills: "
        + SAMPLE_SKILLS
    )
    first = analyze_resume_against_role(text=text, target_role="Backend Developer")
    second = analyze_resume_against_role(text=text, target_role="backend_developer")
    assert first["score"] == second["score"]
    assert first["score_label"] == "Resume Match Score"
    assert "Python" in first["matched_skills"]
    assert isinstance(first["missing_skills"], list)
    assert "intelligence" in first
    assert "roadmap" in first["intelligence"]


def test_resume_matching_via_api(client):
    files = {
        "file": (
            "resume.docx",
            make_resume_docx(SAMPLE_SKILLS),
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    }
    uploaded = client.post("/api/resume/upload", files=files)
    resume_id = uploaded.json()["resume_id"]
    analyzed = client.post(
        "/api/resume/analyze",
        json={"resume_id": resume_id, "target_role": "Backend Developer"},
    )
    assert analyzed.status_code == 200
    body = analyzed.json()
    assert 0 <= body["score"] <= 100
    assert "matched_skills" in body
    assert "improvements" in body
