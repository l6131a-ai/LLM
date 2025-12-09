# ===========================================================================================
# conftest.py - Конфигурация pytest и глобальные фикстуры
# ===========================================================================================
# Этот файл содержит:
# 1. Flask тестовый клиент (для отправки запросов к приложению без реального запуска сервера)
# 2. Фикстуры для мокирования API
# 3. Настройки для всех тестов
# ===========================================================================================

import pytest
import sys
import os

# Добавляем директорию src в путь Python, чтобы можно было импортировать app.py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Импортируем Flask приложение
from app import app


@pytest.fixture
def client():
    """
    Фикстура Flask тестового клиента.
    
    Что это такое?
    ----------------
    Flask тестовый клиент позволяет отправлять HTTP запросы к приложению БЕЗ
    запуска реального веб-сервера. Это очень удобно и быстро.
    
    Как это работает?
    ------------------
    - app.test_client() создает объект, который может отправлять GET/POST запросы
    - Эти запросы обрабатываются приложением "внутри процесса"
    - Нет реального сетевого трафика
    - Тесты работают очень быстро
    
    Параметры:
    -----------
    Нет (автоматически используется глобальный объект app)
    
    Возвращает:
    -----------
    FlaskClient объект для отправки HTTP запросов
    
    Пример использования в тесте:
    ----------------------------
    def test_something(client):
        response = client.post('/', data={'text': 'Hello'})
        assert response.status_code == 200
    """
    
    # Устанавливаем режим тестирования (отключает error catching при обработке запросов)
    app.config['TESTING'] = True
    
    # Создаем тестовый клиент
    with app.test_client() as test_client:
        # Возвращаем клиент для использования в тестах
        yield test_client


@pytest.fixture
def mock_api_key(monkeypatch):
    """
    Фикстура для установки поддельного API ключа в переменные окружения.
    
    Что это такое?
    ----------------
    Эта фикстура использует pytest's monkeypatch для временно установки
    переменной окружения MENTORPIECE_API_KEY на время выполнения теста.
    
    Почему это нужно?
    ------------------
    Наше приложение загружает API ключ из переменной окружения при старте.
    Во время тестирования мы не хотим использовать реальный ключ.
    monkeypatch позволяет "подменить" переменную окружения на время теста.
    
    Параметры:
    -----------
    monkeypatch - встроенная pytest фикстура для изменения переменных окружения
    
    Возвращает:
    -----------
    None (просто устанавливает переменную окружения)
    
    Пример использования:
    --------------------
    def test_with_api_key(mock_api_key):
        # В этом тесте MENTORPIECE_API_KEY уже установлена
        assert os.getenv('MENTORPIECE_API_KEY') == 'test-key-12345'
    """
    
    # Устанавливаем поддельный API ключ для тестов
    # Это значение будет доступно как os.getenv('MENTORPIECE_API_KEY')
    monkeypatch.setenv('MENTORPIECE_API_KEY', 'test-key-12345')
    
    # Код теста выполняется здесь
    # После теста переменная окружения автоматически восстанавливается


@pytest.fixture
def mock_api_response():
    """
    Фикстура с примерами мок-ответов от API.
    
    Что это такое?
    ----------------
    Эта фикстура возвращает словарь с примерами ответов API.
    Это удобно для использования во всех тестах без повторения кода.
    
    Содержимое:
    -----------
    - successful_translation: успешный ответ с переводом
    - successful_verdict: успешный ответ с оценкой качества
    - error_response: ошибка от API
    
    Пример использования:
    --------------------
    def test_translation(mock_api_response):
        expected = mock_api_response['successful_translation']
        assert expected['response'] == 'Some translation'
    """
    
    return {
        'successful_translation': {
            'response': 'Hello, world! This is a translated text.'
        },
        'successful_verdict': {
            'response': 'Translation Quality Score: 9/10\n\nAnalysis:\n- Accuracy: Excellent\n- Grammar: Perfect\n- Fluency: Natural sounding'
        },
        'error_response': {
            'error': 'Internal Server Error',
            'status_code': 500
        },
        'timeout_error': {
            'error': 'Request timeout'
        }
    }
