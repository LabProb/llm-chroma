# tests/test_ping.py
import requests

def test_ping():
    url = "http://127.0.0.1:8000/ping"
    try:
        response = requests.get(url, timeout=5)
        print(f"Status code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        print(f"Response JSON: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_ping()