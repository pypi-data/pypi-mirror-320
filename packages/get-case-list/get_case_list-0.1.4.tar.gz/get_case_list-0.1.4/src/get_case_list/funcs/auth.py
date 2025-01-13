import requests
import socket


def login(username, password):
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        result = requests.post("https://officer.thaipoliceonline.go.th/api/e-form/v1.0/user/auth/police", json={"UserName": username, "Password": password, "IpaAdress": local_ip})

        result = result.json()
        token = result.get("Value", {}).get("Token", "")
        return token
    except Exception as e:
        print("ERROR: wrong username or password")
