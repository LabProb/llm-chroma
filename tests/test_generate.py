# tests/test_generate.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_generate_endpoint():
    prompt = "Розкажи мені щось цікаве про чорні діри"
    response = client.post("/api/generate", json={"prompt": prompt})

    print(f"\nStatus code: {response.status_code}")
    print(f"Response text: {response.text}")

    assert response.status_code == 200
    data = response.json()

    assert "response" in data
    assert "tokens" in data
    assert "duration" in data

    print(f"\nResponse: {data['response']}")
    print(f"Tokens used: {data['tokens']}")
    print(f"Duration: {data['duration']}s")