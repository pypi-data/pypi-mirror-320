import requests
import sys
import textwrap
import time
import importlib.resources

class Client:
    def __init__(self, model='gpt-4o'):
        self.url = 'http://5.35.46.26:10500/chat'
        self.model = model
        self.model_selected = False
        self.system_prompt = ('Всегда форматируй все формулы и символы в Unicode или ASCII.'
                              'Не используй LaTeX или другие специальные вёрстки.'
                              'Пиши по-русски.')

    def select_model(self, force=False):
        if not self.model_selected or force:
            text = """
            Выберите модель: 
            1) gpt-4o
            2) o1-mini
            3) o1-preview
            4) gpt-4o-mini
            """
            print(textwrap.dedent(text).lstrip(), flush=True)
            sys.stdout.flush()
            time.sleep(0.01)
            choice = input('Введите номер варианта: ')
            if choice == '1':
                self.model = 'gpt-4o'
            elif choice == '2':
                self.model = 'o1-mini'
            elif choice == '3':
                self.model = 'o1-preview'
            elif choice == '4':
                self.model = 'gpt-4o-mini'
            else:
                print(f'Напечатайте только цифру от 1 до 4! Используется модель по умолчанию {self.model}\n')

    def get_response(self, message):
        headers = {
            'Content-Type': 'application/json'
        }
        
        if self.model in ['o1-mini', 'o1-preview']:
            messages = [{'role': 'user', 'content': f"{self.system_prompt}\n{message}"}]
        else:
            messages = [
                {'role': 'system', 'content': self.system_prompt},
                {'role': 'user', 'content': message}
            ]

        data = {
            'model': self.model,
            'messages': messages
        }

        response = requests.post(self.url, headers=headers, json=data)
        
        return response.json()['choices'][0]['message']['content']


class ClientManager:
    _client_instance = None

    @classmethod
    def get_client(cls, skip_selection=False):
        if cls._client_instance is None:
            cls._client_instance = Client()
            if not skip_selection:
                cls._client_instance.select_model()
        return cls._client_instance

def read_txt_file(file_name):
    with importlib.resources.open_text('danya.data', file_name) as file:
        content = file.read()
    return content


def ask(message, m=1):
    """
    Отправляет запрос к модели и возвращает ответ.

    Параметры:
        message (str): Текст запроса, который нужно отправить модели.
        m (int): Номер модели, которую нужно использовать. 
                 Поддерживаемые значения:
                 1 - 'gpt-4o'(по умолчанию)
                 2 - 'o1-mini'
                 3 - 'o1-preview'
                 4 - 'gpt-4o-mini'

    Возвращает:
        str: Ответ модели на заданное сообщение.
    """
    model_map = {1: 'gpt-4o', 2: 'o1-mini', 3: 'o1-preview', 4: 'gpt-4o-mini'}
    client = ClientManager.get_client(skip_selection=True)
    assert m in model_map
    if m in model_map:
        client.model = model_map[m]
    return client.get_response(message)

def get(a='д'):
    """
    Возвращает содержимое одного из предопределённых текстовых файлов с ДЗ, семинарами и теорией.

    Параметры:
        a (str): Имя автора файла.
                     - 'а' для Тёмы
                     - 'д' для Дани
                     - 'м' для Миши
    Возвращает:
        str: Содержимое выбранного файла.
    """

    authors = {'а': 'artyom', 'д': 'danya', 'м': 'misha'}
    a = a.lower().replace('d', 'д').replace('a', 'а').replace('m', 'м')
    author_name = authors.get(a, 'danya')
    filename = f"{author_name}_{'c'}.txt"
    
    return read_txt_file(filename)
        
