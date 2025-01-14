from mistralai import Mistral
import pyperclip
import random

api_keys = ['uQwjntCIJ9omN9z8jLTV1VOUvYlbaDIv', 'tgPxn1rFujtuJe1H0j4PQTSjbLthvjyO']
model = "mistral-large-latest"

def get(message):
    """
    Отправляет запрос к Mistral AI и копирует ответ в буфер обмена.

    :param api_keys: Список API ключей для доступа к Mistral AI.
    :param model: Модель, которую нужно использовать.
    :param message: Запрос пользователя.
    """
    # Выбираем случайный API ключ из списка
    api_key = random.choice(api_keys)

    # Инициализируем клиент Mistral AI
    client = Mistral(api_key=api_key)

    # Отправляем запрос
    chat_response = client.chat.complete(
        model=model,
        messages=[
            {
                "role": "user",
                "content": message + " В твоем ответе не должно быть ничего, кроме кода, решающего задачу.",
            },
        ]
    )

    # Получаем ответ
    response_content = chat_response.choices[0].message.content

    # Копируем ответ в буфер обмена
    pyperclip.copy(response_content)

class get_cl:
    def __init__(self, message):
        # Выбираем случайный API ключ из списка
        api_key = random.choice(api_keys)
    
        # Инициализируем клиент Mistral AI
        client = Mistral(api_key=api_key)
    
        # Отправляем запрос
        chat_response = client.chat.complete(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": message + " В твоем ответе не должно быть ничего, кроме кода, решающего задачу.",
                },
            ]
        )
    
        # Получаем ответ
        response_content = chat_response.choices[0].message.content
        
        self.answer = response_content

    @property
    def __doc__(self):
        return self.answer