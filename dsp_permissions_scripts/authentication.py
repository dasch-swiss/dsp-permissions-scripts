import requests


def get_token(host: str, email: str, pw: str) -> str:
    url = f"https://{host}/v2/authentication"
    response = requests.post(url, json={"email": email, "password": pw})
    assert response.status_code == 200
    token: str = response.json()["token"]
    return token
