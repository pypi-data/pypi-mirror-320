import requests
import base64

token = None
username = None
def login():
    global token
    global username
    username = input('usr')
    password = input('pwd')

    credentials = f"{username}:{password}"
    token = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
    headers = {
            "Authorization": f"Bearer {token}",
            'Content-Type': 'application/json'
        }
    try:
        response = requests.post("http://5.35.46.26:10500/get?n=100", headers=headers)
        response.raise_for_status() 

        print("Успешный вход!")
        return True
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 401:  
            print("Неправильный логин или пароль. Попробуйте снова.")
        else:
            print(f"Ошибка сервера: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as req_err:
        print(f"Ошибка подключения или запроса: {req_err}")
    except Exception as err:
        print(f"Произошла ошибка: {err}")

    return False