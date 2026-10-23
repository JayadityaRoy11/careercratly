def test_interview_question_generation(client):
    response = client.get(
        "/api/interview/questions",
        params={"role": "Backend Developer", "difficulty": "easy"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["questions"]
    assert body["questions"][0]["question"]


def test_interview_evaluation(client):
    response = client.post(
        "/api/interview/evaluate",
        json={
            "role": "Backend Developer",
            "question": "What is the difference between PUT and PATCH in a REST API?",
            "answer": (
                "PUT replaces the whole resource and is idempotent. "
                "PATCH applies a partial update. For example you patch one field."
            ),
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert 0 <= body["score"] <= 100
    assert "keyword_coverage" in body
    assert "suggestions" in body
    first = client.post(
        "/api/interview/evaluate",
        json={
            "role": "Backend Developer",
            "question": "What is the difference between PUT and PATCH in a REST API?",
            "answer": (
                "PUT replaces the whole resource and is idempotent. "
                "PATCH applies a partial update. For example you patch one field."
            ),
        },
    ).json()
    assert first["score"] == body["score"]
