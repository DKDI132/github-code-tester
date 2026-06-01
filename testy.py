import requests

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwiZXhwIjoxNzgwNDIyMDY2fQ.Ry7kz3WsfIZSz86qkTSGslQfQipUeMZscU7gdcC2SI0"

response = requests.post(
    "http://localhost:8000/api-operacje/sprawdz",
    headers={
        "Authorization": f"Bearer {token}"
    },
    json={
        "link": "https://github.com/user/projekt"
    }
)

print("Status:", response.status_code)
print("Odpowiedz:", response.text)