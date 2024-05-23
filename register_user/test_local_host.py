import requests

url = "http://localhost:8000/register/"

data = {
    "username": "example_user",
    "email": "example@example.com",
    "password": "example_password"
}

response = requests.post(url, json=data)

if response.status_code == 200:
    print("User successfully registered!")
    print("Response:", response.json())
else:
    print("Failed to register user.")
    print("Response:", response.json())
