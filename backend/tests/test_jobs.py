from tests.conftest import SAMPLE_SKILLS, make_resume_docx


def test_job_filtering(client):
    response = client.get(
        "/api/jobs/search",
        params={"work_mode": "remote", "employment_type": "internship"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["count"] >= 1
    for item in body["items"]:
        assert item["work_mode"] == "remote"
        assert item["employment_type"] == "internship"
        assert item["external_url"].startswith("http")
        assert item["source"] == "mock"


def test_job_matching(client):
    files = {
        "file": (
            "resume.docx",
            make_resume_docx(SAMPLE_SKILLS),
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    }
    resume_id = client.post("/api/resume/upload", files=files).json()["resume_id"]
    response = client.post("/api/jobs/match", json={"resume_id": resume_id})
    assert response.status_code == 200
    items = response.json()["items"]
    assert items
    scores = [job["match_score"] for job in items]
    assert scores == sorted(scores, reverse=True)
    assert "matched_skills" in items[0]
    assert "missing_skills" in items[0]
    assert items[0]["external_url"]


def test_job_sources_not_configured(client):
    response = client.get("/api/jobs/sources")
    assert response.status_code == 200
    providers = {row["provider"]: row for row in response.json()["sources"]}
    assert providers["linkedin"]["status"] == "not_configured"
    assert providers["naukri"]["status"] == "not_configured"
    assert providers["mock"]["status"] == "demo"
    assert providers["linkedin"]["live"] is False

