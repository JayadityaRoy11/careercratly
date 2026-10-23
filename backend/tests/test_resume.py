from tests.conftest import SAMPLE_SKILLS, make_resume_docx, make_resume_pdf


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_pdf_parsing(client):
    files = {"file": ("resume.pdf", make_resume_pdf(SAMPLE_SKILLS), "application/pdf")}
    response = client.post("/api/resume/upload", files=files)
    assert response.status_code == 201
    body = response.json()
    assert body["file_type"] == "pdf"
    assert body["pages"] >= 1
    assert "Python" in body["text"]
    assert body["resume_id"]


def test_docx_parsing(client):
    files = {"file": ("resume.docx", make_resume_docx(SAMPLE_SKILLS), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    response = client.post("/api/resume/upload", files=files)
    assert response.status_code == 201
    body = response.json()
    assert body["file_type"] == "docx"
    assert "Python" in body["text"]


def test_invalid_file_type(client):
    files = {"file": ("notes.txt", b"hello", "text/plain")}
    response = client.post("/api/resume/upload", files=files)
    assert response.status_code == 415
    assert "error" in response.json()
    assert response.json()["error"]["code"] == "unsupported_type"


def test_missing_resume_analyze(client):
    response = client.post(
        "/api/resume/analyze",
        json={"resume_id": "00000000-0000-0000-0000-000000000001", "target_role": "Backend Developer"},
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"
