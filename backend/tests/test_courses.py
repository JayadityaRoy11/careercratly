def test_course_recommendation(client):
    response = client.get("/api/courses/recommend", params=[("skills", "Python"), ("skills", "Docker")])
    assert response.status_code == 200
    body = response.json()
    assert len(body["recommendations"]) == 2
    python_group = next(item for item in body["recommendations"] if item["skill"] == "Python")
    assert 1 <= len(python_group["courses"]) <= 3
    assert python_group["courses"][0]["url"].startswith("http")


def test_project_resources(client):
    response = client.get("/api/projects/resources", params={"topic": "RAG chatbot over a document corpus"})
    assert response.status_code == 200
    body = response.json()
    assert body["resources"]
    assert body["resources"][0]["url"].startswith("http")
