# ===========================================================================================
# test_app.py - Юнит-тесты для Flask приложения "AI Translator & Critic"
# ===========================================================================================
# Этот файл содержит набор тестов для проверки:
# 1. Загрузки API ключа из переменных окружения
# 2. Успешного выполнения функции call_llm
# 3. Обработки ошибок при работе с API
# 4. Корректной обработки HTTP методов (GET/POST)
#
# Фреймворк: pytest
# Моки: unittest.mock.patch (для подмены реальных HTTP запросов)
# ===========================================================================================

import pytest
import os
from unittest.mock import patch, MagicMock
import sys

# Добавляем src в путь для импорта приложения
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))


# ===========================================================================================
# ТЕСТ 1: ПРОВЕРКА ЗАГРУЗКИ API КЛЮЧА ИЗ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ
# ===========================================================================================

class TestAPIKeyLoading:
    """
    Класс TestAPIKeyLoading содержит тесты для проверки корректной загрузки API ключа.
    
    Что это за класс?
    -------------------
    В pytest тесты можно группировать в классы. Это удобно для организации
    связанных тестов. Например, все тесты, связанные с API ключом, собраны здесь.
    
    Преимущества:
    - Код лучше организован
    - Легче находить нужные тесты
    - Можно использовать setup/teardown методы для инициализации перед каждым тестом
    """
    
    def test_api_key_loaded_from_env(self, mock_api_key):
        """
        ТЕСТ: Проверка, что API ключ загружается из переменной окружения.
        
        Сценарий:
        ---------
        1. Фикстура mock_api_key устанавливает MENTORPIECE_API_KEY='test-key-12345'
        2. Проверяем, что переменная окружения содержит установленное значение
        
        Ожидаемый результат:
        --------------------
        os.getenv('MENTORPIECE_API_KEY') должен вернуть 'test-key-12345'
        
        Тип теста: POSITIVE TEST (проверяем, что всё работает как надо)
        """
        
        # Получаем значение API ключа из переменной окружения
        api_key = os.getenv('MENTORPIECE_API_KEY')
        
        # Проверяем, что ключ не пуст и имеет ожидаемое значение
        assert api_key is not None, "API ключ не должен быть None"
        assert api_key == 'test-key-12345', f"Ожидался 'test-key-12345', получен '{api_key}'"
        
        print(f"✅ API ключ успешно загружен: {api_key}")
    
    
    def test_api_key_missing_handling(self):
        """
        ТЕСТ: Проверка поведения при отсутствии API ключа.
        
        Сценарий:
        ---------
        1. Используем monkeypatch через встроенный fixture для удаления API ключа
        2. Вызываем os.getenv('MENTORPIECE_API_KEY')
        3. Проверяем, что функция корректно обрабатывает отсутствие ключа
        
        Ожидаемый результат:
        --------------------
        os.getenv должен вернуть None (или значение по умолчанию)
        
        Тип теста: NEGATIVE TEST (проверяем обработку ошибок)
        """
        
        # Мокируем ситуацию, где переменная окружения не установлена
        with patch.dict(os.environ, {}, clear=True):
            # Получаем значение несуществующей переменной
            api_key = os.getenv('MENTORPIECE_API_KEY')
            
            # Проверяем, что функция вернула None (значение по умолчанию)
            assert api_key is None, "Несуществующая переменная окружения должна быть None"
        
        print("✅ Отсутствие API ключа корректно обработано")


# ===========================================================================================
# ТЕСТ 2: ПРОВЕРКА УСПЕШНОГО ВЫПОЛНЕНИЯ ФУНКЦИИ call_llm
# ===========================================================================================

class TestCallLLMFunction:
    """
    Класс TestCallLLMFunction содержит тесты для функции call_llm.
    
    Что тестируем?
    ---------------
    Функция call_llm отправляет HTTP POST запрос к внешнему API.
    Нам нужно проверить, что она:
    1. Отправляет правильный запрос
    2. Обрабатывает ответ правильно
    3. Обрабатывает ошибки корректно
    """
    
    @patch('app.requests.post')
    def test_successful_llm_call(self, mock_post, mock_api_key, mock_api_response):
        """
        ТЕСТ: Проверка успешного выполнения функции call_llm.
        
        Что такое @patch?
        ------------------
        @patch - это декоратор, который "подменяет" реальную функцию на mock-объект.
        В нашем случае:
        - @patch('app.requests.post') подменяет requests.post
        - Это значит, что реальный HTTP запрос НЕ будет отправлен
        - Вместо этого будет использован mock-объект
        - Тест будет очень быстрым и не будет тратить токены API
        
        Параметр mock_post:
        --------------------
        mock_post - это mock-объект, который заменяет requests.post
        Мы можем настроить его поведение:
        - mock_post.return_value = ... (что он будет возвращать)
        - mock_post.assert_called_with(...) (проверить, как его вызывали)
        
        Сценарий:
        ---------
        1. Импортируем функцию call_llm из приложения
        2. Настраиваем mock_post для возвращения успешного ответа
        3. Вызываем call_llm
        4. Проверяем:
           - Что функция вернула правильный результат
           - Что requests.post был вызван с правильными параметрами
        
        Ожидаемый результат:
        --------------------
        Функция должна вернуть текст перевода из ответа API
        """
        
        # Импортируем функцию, которую тестируем
        from app import call_llm
        
        # Получаем мок-ответ из фикстуры
        expected_response = mock_api_response['successful_translation']
        
        # Настраиваем mock-объект request.post:
        # Когда requests.post будет вызван, он вернет mock-объект response
        mock_response = MagicMock()
        mock_response.status_code = 200  # Успешный статус код
        mock_response.json.return_value = expected_response  # Возвращаемый JSON
        
        # Устанавливаем return_value для mock_post
        mock_post.return_value = mock_response
        
        # Вызываем функцию call_llm
        # Она будет использовать мокированный requests.post
        result = call_llm(
            model_name='Qwen/Qwen3-VL-30B-A3B-Instruct',
            messages='Переведи: Hello, world!'
        )
        
        # Проверяем результат
        assert result == expected_response['response'], \
            f"Ожидалось '{expected_response['response']}', получено '{result}'"
        
        # Проверяем, что requests.post был вызван с правильными параметрами
        mock_post.assert_called_once()
        
        # Получаем аргументы, с которыми был вызван requests.post
        call_args = mock_post.call_args
        
        # Проверяем URL
        assert call_args[0][0] == 'https://api.mentorpiece.org/v1/process-ai-request', \
            "URL должен быть правильным"
        
        # Проверяем заголовки (Authorization header)
        headers = call_args[1]['headers']
        assert 'Authorization' in headers, "Заголовок Authorization должен быть в запросе"
        assert headers['Authorization'].startswith('Bearer '), \
            "Authorization заголовок должен начинаться с 'Bearer '"
        
        print("✅ Функция call_llm успешно отправляет и обрабатывает запрос")
    
    
    @patch('app.requests.post')
    def test_llm_call_with_timeout_error(self, mock_post, mock_api_key):
        """
        ТЕСТ: Проверка обработки ошибки таймаута при запросе к API.
        
        Что такое timeout?
        ------------------
        Timeout - это ошибка, которая происходит, когда приложение слишком долго
        ждет ответ от сервера. По умолчанию в нашем коде это 30 секунд.
        
        Сценарий:
        ---------
        1. Настраиваем mock_post для выброса исключения Timeout
        2. Вызываем call_llm
        3. Проверяем, что функция перехватила исключение и вернула ошибку
        
        Ожидаемый результат:
        --------------------
        Функция должна вернуть сообщение об ошибке (не упасть)
        """
        
        from app import call_llm
        import requests
        
        # Настраиваем mock_post для выброса Timeout исключения
        mock_post.side_effect = requests.exceptions.Timeout(
            "Connection timed out"
        )
        
        # Вызываем функцию (она не должна упасть)
        result = call_llm(
            model_name='Qwen/Qwen3-VL-30B-A3B-Instruct',
            messages='Test message'
        )
        
        # Проверяем, что вернулось сообщение об ошибке
        assert result is not None, "Результат не должен быть None"
        assert isinstance(result, str), "Результат должен быть строкой"
        assert 'Таймаут' in result or 'Timeout' in result or 'ошибка' in result.lower(), \
            "Результат должен содержать указание на ошибку"
        
        print(f"✅ Таймаут ошибка корректно обработана: {result}")
    
    
    @patch('app.requests.post')
    def test_llm_call_with_connection_error(self, mock_post, mock_api_key):
        """
        ТЕСТ: Проверка обработки ошибки подключения при запросе к API.
        
        Что такое ConnectionError?
        --------------------------
        ConnectionError - это ошибка, которая происходит, когда приложение не может
        подключиться к серверу (например, сервер недоступен или нет интернета).
        
        Сценарий:
        ---------
        1. Настраиваем mock_post для выброса исключения ConnectionError
        2. Вызываем call_llm
        3. Проверяем, что функция перехватила исключение и вернула ошибку
        
        Ожидаемый результат:
        --------------------
        Функция должна вернуть сообщение об ошибке подключения
        """
        
        from app import call_llm
        import requests
        
        # Настраиваем mock_post для выброса ConnectionError
        mock_post.side_effect = requests.exceptions.ConnectionError(
            "Failed to establish a new connection"
        )
        
        # Вызываем функцию (она не должна упасть)
        result = call_llm(
            model_name='claude-sonnet-4-5-20250929',
            messages='Test message'
        )
        
        # Проверяем, что вернулось сообщение об ошибке подключения
        assert result is not None, "Результат не должен быть None"
        assert isinstance(result, str), "Результат должен быть строкой"
        assert 'подключи' in result.lower() or 'connection' in result.lower(), \
            "Результат должен содержать указание на ошибку подключения"
        
        print(f"✅ Ошибка подключения корректно обработана: {result}")
    
    
    @patch('app.requests.post')
    def test_llm_call_with_auth_error(self, mock_post, mock_api_key):
        """
        ТЕСТ: Проверка обработки ошибки аутентификации (401) при запросе к API.
        
        Что такое 401 Unauthorized?
        ----------------------------
        401 - это HTTP статус код, который означает, что запрос не авторизован.
        Обычно это происходит, когда:
        - API ключ неверный
        - API ключ истек
        - Ключ не был отправлен в заголовке Authorization
        
        Сценарий:
        ---------
        1. Настраиваем mock_post для возврата статуса 401
        2. Вызываем call_llm
        3. Проверяем, что функция корректно обработала ошибку
        
        Ожидаемый результат:
        --------------------
        Функция должна вернуть сообщение об ошибке 401
        """
        
        from app import call_llm
        
        # Настраиваем mock_response с ошибкой 401
        mock_response = MagicMock()
        mock_response.status_code = 401  # Unauthorized
        mock_response.text = "Invalid API Key"
        
        mock_post.return_value = mock_response
        
        # Вызываем функцию
        result = call_llm(
            model_name='Qwen/Qwen3-VL-30B-A3B-Instruct',
            messages='Test message'
        )
        
        # Проверяем результат
        assert isinstance(result, str), "Результат должен быть строкой"
        assert '401' in result or 'ошибка' in result.lower(), \
            "Результат должен содержать код ошибки или слово 'ошибка'"
        
        print(f"✅ Ошибка аутентификации (401) корректно обработана: {result}")


# ===========================================================================================
# ТЕСТ 3: ПРОВЕРКА GET И POST МАРШРУТОВ ПРИЛОЖЕНИЯ
# ===========================================================================================

class TestHTTPRoutes:
    """
    Класс TestHTTPRoutes содержит тесты для HTTP маршрутов (GET и POST).
    
    Что тестируем?
    ---------------
    Мы тестируем:
    1. GET / - отображает форму
    2. POST / - обрабатывает отправку формы и вызывает call_llm
    """
    
    def test_get_root_route(self, client):
        """
        ТЕСТ: Проверка GET запроса на главную страницу.
        
        Что такое client?
        ------------------
        client - это Flask тестовый клиент из фикстуры conftest.py
        Он позволяет отправлять HTTP запросы к приложению без реального веб-сервера
        
        Сценарий:
        ---------
        1. Отправляем GET запрос на /
        2. Проверяем статус код 200 (успешно)
        3. Проверяем, что в ответе содержится HTML форма
        
        Ожидаемый результат:
        --------------------
        - Статус код: 200
        - В HTML содержится textarea с id='original_text'
        - В HTML содержится select с id='target_language'
        """
        
        # Отправляем GET запрос на главную страницу
        response = client.get('/')
        
        # Проверяем статус код
        assert response.status_code == 200, \
            f"Ожидался статус 200, получен {response.status_code}"
        
        # Получаем текст ответа (HTML)
        html_content = response.get_data(as_text=True)
        
        # Проверяем, что в HTML содержится форма
        assert 'original_text' in html_content, \
            "В HTML должно быть поле original_text (textarea)"
        assert 'target_language' in html_content, \
            "В HTML должно быть поле target_language (select)"
        assert 'Перевести' in html_content, \
            "В HTML должна быть кнопка 'Перевести'"
        
        print("✅ GET запрос на / успешно возвращает форму")
    
    
    @patch('app.call_llm')
    def test_post_with_valid_data(self, mock_call_llm, client, mock_api_response):
        """
        ТЕСТ: Проверка POST запроса с валидными данными.
        
        Что такое mock_call_llm?
        -------------------------
        В этом тесте мы мокируем функцию call_llm, чтобы не делать реальные
        запросы к API. Вместо этого function вернет мок-ответ.
        
        Сценарий:
        ---------
        1. Настраиваем mock_call_llm для возврата мок-ответов
        2. Отправляем POST запрос с текстом и языком
        3. Проверяем, что функция call_llm была вызвана 2 раза:
           - Первый раз для перевода (Qwen модель)
           - Второй раз для оценки (Claude модель)
        4. Проверяем, что в ответе содержатся результаты
        
        Ожидаемый результат:
        --------------------
        - Статус код: 200
        - В HTML содержатся исходный текст, перевод и оценка
        """
        
        # Настраиваем mock_call_llm для возврата разных значений при разных вызовах
        mock_call_llm.side_effect = [
            mock_api_response['successful_translation']['response'],  # Первый вызов (перевод)
            mock_api_response['successful_verdict']['response']  # Второй вызов (оценка)
        ]
        
        # Отправляем POST запрос с данными формы
        response = client.post('/', data={
            'original_text': 'Привет, мир!',
            'target_language': 'Английский'
        })
        
        # Проверяем статус код
        assert response.status_code == 200, \
            f"Ожидался статус 200, получен {response.status_code}"
        
        # Проверяем, что call_llm был вызван 2 раза
        assert mock_call_llm.call_count == 2, \
            f"call_llm должна быть вызвана 2 раза, была вызвана {mock_call_llm.call_count} раз"
        
        # Проверяем параметры первого вызова (для перевода)
        first_call = mock_call_llm.call_args_list[0]
        assert 'Qwen' in first_call[1]['model_name'], \
            "Первый вызов должен быть с моделью Qwen"
        
        # Проверяем параметры второго вызова (для оценки)
        second_call = mock_call_llm.call_args_list[1]
        assert 'claude' in second_call[1]['model_name'].lower(), \
            "Второй вызов должен быть с моделью Claude"
        
        # Получаем текст ответа
        html_content = response.get_data(as_text=True)
        
        # Проверяем, что в ответе содержатся результаты
        assert 'Привет, мир!' in html_content, \
            "В ответе должен содержаться исходный текст"
        assert 'Hello' in html_content or 'translated' in html_content.lower(), \
            "В ответе должен содержаться перевод"
        
        print("✅ POST запрос с валидными данными успешно обработан")
    
    
    def test_post_with_empty_text(self, client):
        """
        ТЕСТ: Проверка POST запроса с пустым текстом.
        
        Сценарий:
        ---------
        1. Отправляем POST запрос с пустым текстом
        2. Проверяем, что приложение возвращает ошибку
        
        Ожидаемый результат:
        --------------------
        - Статус код: 200 (форма остается на странице)
        - В ответе содержится сообщение об ошибке
        """
        
        # Отправляем POST запрос с пустым текстом
        response = client.post('/', data={
            'original_text': '',  # Пустой текст
            'target_language': 'Английский'
        })
        
        # Проверяем статус код
        assert response.status_code == 200, \
            f"Ожидался статус 200, получен {response.status_code}"
        
        # Получаем текст ответа
        html_content = response.get_data(as_text=True)
        
        # Проверяем, что содержится сообщение об ошибке
        assert 'ошибка' in html_content.lower() or '❌' in html_content, \
            "В ответе должно быть сообщение об ошибке"
        
        print("✅ POST запрос с пустым текстом корректно обработан")


# ===========================================================================================
# ЗАПУСК ТЕСТОВ
# ===========================================================================================

if __name__ == '__main__':
    """
    Если запустить этот файл напрямую (python test_app.py),
    то будут запущены все тесты.
    
    Однако рекомендуется запускать тесты через pytest:
    pytest tests/unit/test_app.py -v
    """
    
    pytest.main([__file__, '-v'])
