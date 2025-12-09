# ===========================================================================================
# Flask Web Application: "AI Translator & Critic"
# ===========================================================================================
# Описание: Приложение для перевода текста с использованием AI и оценки качества перевода
# Используемые технологии: Flask, requests, python-dotenv
# API: https://api.mentorpiece.org/v1/process-ai-request
# ===========================================================================================

# Импортируем необходимые библиотеки
from flask import Flask, render_template, request, jsonify
import requests  # Для выполнения HTTP-запросов к LLM API
import os  # Для работы с переменными окружения
from dotenv import load_dotenv  # Для загрузки API ключа из файла .env

# ===========================================================================================
# ИНИЦИАЛИЗАЦИЯ
# ===========================================================================================

# Загружаем переменные окружения из файла .env
load_dotenv()

# Создаем Flask приложение
app = Flask(__name__)

# Загружаем API ключ из переменной окружения
# API_KEY хранится в файле .env и загружается безопасно (не через код)
API_KEY = os.getenv("MENTORPIECE_API_KEY")

# URL API endpoint для отправки запросов к LLM модели
API_ENDPOINT = "https://api.mentorpiece.org/v1/process-ai-request"

# ===========================================================================================
# ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ ДЛЯ РАБОТЫ С API
# ===========================================================================================

def call_llm(model_name, messages):
    """
    Вспомогательная функция для отправки запроса к LLM API.
    
    Параметры:
    -----------
    model_name : str
        Имя используемой модели (например, "Qwen/Qwen3-VL-30B-A3B-Instruct")
    
    messages : str
        Текст запроса/промпта для отправки в LLM
    
    Возвращает:
    -----------
    str
        Текст ответа от LLM или сообщение об ошибке
    
    Обработка ошибок:
    -----------------
    - Ловит исключения сетевых ошибок (requests.RequestException)
    - Ловит ошибки 4xx и 5xx (проверяет response.status_code)
    - Возвращает понятное сообщение об ошибке пользователю
    """
    
    try:
        # Проверяем наличие API ключа перед отправкой запроса
        if not API_KEY:
            return "❌ Ошибка: API ключ не загружен. Проверьте файл .env и переменную MENTORPIECE_API_KEY"
        
        # Подготавливаем заголовки HTTP запроса
        # Authorization: Bearer <API_KEY> - стандартный способ передачи ключа в заголовке
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"  # Указываем, что отправляем JSON
        }
        
        # Подготавливаем тело запроса в формате JSON
        # Формат соответствует требованиям API: { "model_name": "", "prompt": "" }
        payload = {
            "model_name": model_name,
            "prompt": messages  # messages передается как prompt в API
        }
        
        # Отправляем POST запрос к API endpoint
        # timeout=30 - ограничиваем время ожидания ответа 30 секундами
        response = requests.post(
            API_ENDPOINT,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        # Проверяем статус код ответа
        # Если статус 200-299 - успешный ответ, иначе это ошибка
        if response.status_code >= 400:
            # Логируем ошибку для отладки (QA специалисты могут видеть это в логах)
            error_message = f"API вернул ошибку: {response.status_code}"
            if response.text:
                error_message += f" - {response.text}"
            print(f"⚠️  {error_message}")
            return f"❌ Ошибка API (код {response.status_code}): Сервер не смог обработать запрос"
        
        # Парсим JSON ответ от API
        # API возвращает формат: { "response": "текст ответа" }
        response_json = response.json()
        
        # Извлекаем текст ответа из поля "response"
        result = response_json.get("response", "❌ Ошибка: ответ API не содержит поле 'response'")
        
        return result
    
    # Обработка сетевых ошибок (соединение потеряно, таймаут и т.д.)
    except requests.exceptions.Timeout:
        error_msg = "❌ Ошибка: Таймаут при подключении к серверу. Сервер слишком долго отвечал (>30 сек)"
        print(f"⚠️  {error_msg}")
        return error_msg
    
    except requests.exceptions.ConnectionError:
        error_msg = "❌ Ошибка: Не удалось подключиться к серверу. Проверьте интернет-соединение и URL API"
        print(f"⚠️  {error_msg}")
        return error_msg
    
    except requests.exceptions.RequestException as e:
        error_msg = f"❌ Ошибка при отправке запроса: {str(e)}"
        print(f"⚠️  {error_msg}")
        return error_msg
    
    # Обработка ошибок парсинга JSON
    except ValueError as e:
        error_msg = f"❌ Ошибка: Сервер вернул некорректный JSON. Детали: {str(e)}"
        print(f"⚠️  {error_msg}")
        return error_msg
    
    # Ловим все остальные непредвиденные ошибки
    except Exception as e:
        error_msg = f"❌ Неожиданная ошибка: {str(e)}"
        print(f"⚠️  {error_msg}")
        return error_msg


# ===========================================================================================
# МАРШРУТЫ (ROUTES) ПРИЛОЖЕНИЯ
# ===========================================================================================

@app.route("/", methods=["GET"])
def index_get():
    """
    Обработчик GET запроса на главную страницу.
    
    Метод: GET
    Роль: Отображает форму для ввода текста и выбора языка
    
    Возвращает:
    -----------
    HTML страница (templates/index.html) с пустой формой
    """
    
    # Рендерим HTML шаблон
    # render_template ищет файл в папке templates/
    # При GET запросе мы передаем None для всех переменных (нет данных для отображения)
    return render_template(
        "index.html",
        original_text=None,
        translated_text=None,
        quality_verdict=None
    )


@app.route("/", methods=["POST"])
def index_post():
    """
    Обработчик POST запроса для перевода и оценки текста.
    
    Метод: POST
    Роль: Получает текст и язык из формы, выполняет перевод и оценку качества
    
    Шаги обработки:
    ----------------
    1. Извлекаем данные из POST формы (текст и язык)
    2. Вызываем LLM для перевода текста
    3. Вызываем LLM для оценки качества перевода (LLM-as-a-Judge)
    4. Рендерим результаты в HTML шаблон
    
    Возвращает:
    -----------
    HTML страница (templates/index.html) с результатами перевода и оценки
    """
    
    # Извлекаем данные из HTML формы
    # request.form содержит все данные, отправленные методом POST
    original_text = request.form.get("original_text", "").strip()
    target_language = request.form.get("target_language", "English").strip()
    
    # Проверяем, что пользователь ввел текст (не оставил поле пустым)
    if not original_text:
        # Возвращаем форму с сообщением об ошибке
        return render_template(
            "index.html",
            original_text="",
            translated_text="❌ Ошибка: Пожалуйста, введите текст для перевода",
            quality_verdict=None
        )
    
    # ==========================================
    # ШАГ 1: ПЕРЕВОД ТЕКСТА
    # ==========================================
    
    # Создаем промпт (инструкцию) для модели-переводчика
    # Промпт должен быть детальным и понятным для LLM
    translation_prompt = f"""Переведи следующий текст на {target_language}. 
Возвращай ТОЛЬКО перевод без комментариев и объяснений.

Исходный текст:
{original_text}"""
    
    # Вызываем функцию call_llm для выполнения перевода
    # Используем модель Qwen/Qwen3-VL-30B-A3B-Instruct для перевода
    translated_text = call_llm(
        model_name="Qwen/Qwen3-VL-30B-A3B-Instruct",
        messages=translation_prompt
    )
    
    # ==========================================
    # ШАГ 2: ОЦЕНКА КАЧЕСТВА ПЕРЕВОДА
    # ==========================================
    
    # Создаем промпт для оценки качества перевода (LLM-as-a-Judge)
    # Инструкция должна быть четкой и понятной для оценки
    quality_prompt = f"""Оцени качество следующего перевода от 1 до 10 и подробно аргументируй оценку.

Исходный текст:
{original_text}

Перевод на {target_language}:
{translated_text}

Оценка должна включать:
- Точность передачи смысла
- Грамматическую корректность
- Естественность звучания
- Сохранение стиля оригинала

Формат ответа:
Оценка: [число]
Аргументация: [подробный анализ]"""
    
    # Вызываем функцию call_llm для оценки качества
    # Используем модель claude-sonnet-4-5-20250929 для оценки (лучше для анализа)
    quality_verdict = call_llm(
        model_name="claude-sonnet-4-5-20250929",
        messages=quality_prompt
    )
    
    # ==========================================
    # ШАГ 3: ВОЗВРАТ РЕЗУЛЬТАТОВ
    # ==========================================
    
    # Рендерим HTML шаблон с результатами
    # Передаем три переменные для отображения:
    # - original_text: исходный текст
    # - translated_text: переведенный текст
    # - quality_verdict: оценка качества от LLM
    return render_template(
        "index.html",
        original_text=original_text,
        translated_text=translated_text,
        quality_verdict=quality_verdict
    )


# ===========================================================================================
# ЗАПУСК ПРИЛОЖЕНИЯ
# ===========================================================================================

if __name__ == "__main__":
    # debug=True включает:
    # - Автоперезагрузку при изменении кода
    # - Подробные сообщения об ошибках
    # - Интерактивный отладчик
    # В production режиме нужно установить debug=False
    app.run(
        host="0.0.0.0",  # Приложение доступно на всех сетевых интерфейсах
        port=5000,        # Используем стандартный порт Flask
        debug=True        # Режим отладки включен для разработки
    )
