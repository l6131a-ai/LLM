# 🧪 ИНСТРУКЦИЯ ПО ЗАПУСКУ ТЕСТОВ

## Быстрый старт

### 1️⃣ Установка зависимостей

```bash
# Python зависимости
pip install -r requirements.txt

# Node.js зависимости (для Cypress)
npm install
```

### 2️⃣ Запуск приложения

```bash
# В отдельном терминале запустите Flask приложение
python src/app.py

# Приложение будет доступно на http://localhost:5000
```

### 3️⃣ Запуск тестов

#### Вариант A: Юнит-тесты (быстро, 5-10 сек)

```bash
# Все тесты
pytest tests/ -v

# Только unit тесты
pytest tests/unit/ -v

# С подробным выводом
pytest tests/ -v -s

# Конкретный тест
pytest tests/unit/test_app.py::TestAPIKeyLoading::test_api_key_loaded_from_env -v
```

#### Вариант B: UI-тесты (Cypress)

```bash
# Интерактивный режим (рекомендуется)
npx cypress open
# Откроется Cypress Test Runner - выберите тест и смотрите как он выполняется

# Или запустить все тесты в фоне
npx cypress run

# В конкретном браузере
npx cypress run --browser chrome
```

#### Вариант C: Все тесты с npm скриптами

```bash
npm test                    # Все юнит-тесты
npm run cypress:run         # Все UI-тесты
npm run test:coverage       # Юнит-тесты с отчетом о покрытии
```

---

## 📊 Ожидаемые результаты

### Успешный запуск юнит-тестов:

```
tests/unit/test_app.py::TestAPIKeyLoading::test_api_key_loaded_from_env PASSED
tests/unit/test_app.py::TestAPIKeyLoading::test_api_key_missing_handling PASSED
tests/unit/test_app.py::TestCallLLMFunction::test_successful_llm_call PASSED
tests/unit/test_app.py::TestCallLLMFunction::test_llm_call_with_timeout_error PASSED
tests/unit/test_app.py::TestCallLLMFunction::test_llm_call_with_connection_error PASSED
tests/unit/test_app.py::TestCallLLMFunction::test_llm_call_with_auth_error PASSED
tests/unit/test_app.py::TestHTTPRoutes::test_get_root_route PASSED
tests/unit/test_app.py::TestHTTPRoutes::test_post_with_valid_data PASSED
tests/unit/test_app.py::TestHTTPRoutes::test_post_with_empty_text PASSED

============== 9 passed in 1.23s ==============
✅ Все юнит-тесты успешно пройдены!
```

### Успешный запуск UI-тестов:

```
✅ AI Translator & Critic - Основные сценарии
  ✅ Должен успешно выполнить перевод и оценку качества (2.5s)
  ✅ Должен обработать ошибку API 500 и показать сообщение об ошибке (1.2s)
  ✅ Должен сохранять значения в форме после отправки (1.8s)
  ✅ Должен показать ошибку при попытке отправить пустое поле (0.8s)
  ✅ Должен корректно обрабатывать асинхронные запросы (3.0s)

All tests passed! (5 of 5) ✅
```

---

## 🔍 Что тестируется?

### Юнит-тесты (9 тестов)

| Тест | Описание | Файл |
|------|---------|------|
| `test_api_key_loaded_from_env` | API ключ загружается из окружения | test_app.py:38 |
| `test_api_key_missing_handling` | Обработка отсутствия API ключа | test_app.py:66 |
| `test_successful_llm_call` | Успешный запрос к API | test_app.py:108 |
| `test_llm_call_with_timeout_error` | Обработка таймаута | test_app.py:176 |
| `test_llm_call_with_connection_error` | Обработка ошибки подключения | test_app.py:208 |
| `test_llm_call_with_auth_error` | Обработка ошибки 401 | test_app.py:241 |
| `test_get_root_route` | GET / возвращает форму | test_app.py:280 |
| `test_post_with_valid_data` | POST с валидными данными | test_app.py:312 |
| `test_post_with_empty_text` | POST с пустым текстом | test_app.py:359 |

### UI-тесты (5 тестов)

| Тест | Описание | Файл |
|------|---------|------|
| Успешный перевод и оценка | Полный цикл перевода и оценки | translator_critic.cy.js:71 |
| Обработка ошибки API 500 | Ошибка показывается пользователю | translator_critic.cy.js:176 |
| Сохранение значений | Значения остаются в форме | translator_critic.cy.js:221 |
| Валидация пустого поля | Ошибка при пустом поле | translator_critic.cy.js:259 |
| Асинхронная обработка | Корректная работа с задержками | translator_critic.cy.js:291 |

---

## 🛠️ Команды для разработки

### Во время разработки (TDD подход)

```bash
# Запустить тесты в watch режиме (перезапускаются при изменении файлов)
pytest tests/ -v --tb=short -x

# Или для Cypress
npx cypress run --headless --watch
```

### Перед коммитом

```bash
# Запустить все тесты
pytest tests/ -v
npx cypress run

# Проверить код на синтаксис
python -m py_compile src/app.py

# Проверить покрытие кода
pytest tests/ --cov=src --cov-report=term-missing
```

### В CI/CD (GitHub Actions)

```bash
# Установить зависимости
pip install -r requirements.txt
npm install

# Запустить юнит-тесты
pytest tests/unit/ -v

# Запустить UI-тесты
npx cypress run
```

---

## 📝 Файлы тестов

```
LLM/
├── tests/
│   ├── __init__.py
│   ├── conftest.py                 # Фикстуры и конфигурация
│   └── unit/
│       ├── __init__.py
│       └── test_app.py             # 9 юнит-тестов
│
├── cypress/
│   ├── cypress.config.js           # Конфигурация Cypress
│   └── e2e/
│       └── translator_critic.cy.js  # 5 UI-тестов
│
├── TESTING_DOCUMENTATION.md        # Подробная документация
├── TEST_CASES.md                   # Ручные тест-кейсы для QA
├── package.json                    # NPM конфигурация
└── requirements.txt                # Python зависимости
```

---

## ✅ Чеклист перед релизом

- [ ] Все юнит-тесты зеленые (`pytest tests/ -v`)
- [ ] Все UI-тесты зеленые (`npx cypress run`)
- [ ] Покрытие кода > 80% (`pytest --cov`)
- [ ] Нет warning'ов в консоли
- [ ] Приложение работает на localhost:5000
- [ ] API ключ установлен в .env
- [ ] .env файл НЕ закоммичен в Git
- [ ] README актуален

---

## 🔗 Полезные команды

```bash
# Очистить кеш pytest
pytest --cache-clear

# Запустить тесты параллельно
pytest tests/ -n auto

# Сгенерировать HTML отчет
pytest tests/ --html=report.html --self-contained-html

# Отладить конкретный тест
pytest tests/unit/test_app.py::TestAPIKeyLoading -v -s --pdb

# Cypress с видеозаписью
npx cypress run --record
```

---

## 📖 Справка по Cypress

### cy.visit() - переход на страницу
```javascript
cy.visit('/')                    // Переход на baseUrl (localhost:5000)
cy.visit('/about')              // Переход на localhost:5000/about
cy.visit('https://example.com') // Переход на другой сайт
```

### cy.get() - поиск элемента
```javascript
cy.get('#myId')                 // По ID
cy.get('.myClass')              // По классу
cy.get('input[type="text"]')    // По атрибуту
cy.get('[data-testid="btn"]')   // По data-testid
```

### cy.intercept() - мокирование API
```javascript
cy.intercept('GET', '/api/users', { data: [] })  // Простой мок
cy.intercept('POST', '/api/**', (req) => {       // С функцией
  req.reply({ body: { success: true } })
}).as('postRequest')
```

### .should() - проверка условий
```javascript
.should('be.visible')           // Элемент видим
.should('have.value', 'text')   // Значение поля
.should('contain', 'Hello')     // Содержит текст
.should('be.enabled')           // Кнопка активна
```

---

**Последний обновлен:** 2024  
**Версия:** 1.0
