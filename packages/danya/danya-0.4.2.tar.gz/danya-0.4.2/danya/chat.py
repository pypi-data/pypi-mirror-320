import requests
from datetime import datetime

BASE_URL = "5.35.46.26:10500"
SEND_URL = f"http://{BASE_URL}//send"
GET_URL = f"http://{BASE_URL}//get"
HEADERS = {"Content-Type": "application/json"}

def send(username, content):
    """
    Отправляет сообщение в чат.

    Аргументы:
        username (str): Имя пользователя, отправляющего сообщение.
        content (str): Содержимое сообщения.

    Возвращает:
        int | None: Идентификатор сообщения, если успешно, иначе None.
    """
    response = requests.post(SEND_URL, headers=HEADERS, json={"username": username, "content": content})
    if response.status_code == 200:
        msg_id = response.json().get("message_id")
        return msg_id
    print(f"Ошибка при отправке сообщения: {response.text}")
    return None

def hist(last_id=None, n=10):
    """
    Выводит историю сообщений из чата.

    Аргументы:
        last_id (int, optional): Идентификатор последнего сообщения для фильтрации. По умолчанию None.
        n (int, optional): Количество сообщений для отображения. По умолчанию 10.

    Возвращает:
        int | None: Идентификатор последнего сообщения, если успешно, иначе None.
    """
    payload = {"last_id": last_id} if last_id else {}
    response = requests.post(GET_URL, headers=HEADERS, json=payload)
    
    if response.status_code == 200:
        msgs = response.json()

        if last_id is not None:
            msgs = [msg for msg in msgs if msg['id'] > last_id]

        selected = msgs[-n:] if msgs else []

        for msg in selected:
            try:
                ts = datetime.fromisoformat(msg['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                ts = msg['timestamp']
            print(f"[{ts}] {msg['username']}: {msg['content']}")

        return selected[-1]['id'] if selected else last_id
    
    print(f"Ошибка при получении сообщений: {response.text}")
    return last_id
