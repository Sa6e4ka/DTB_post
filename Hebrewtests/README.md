# Hebrew Learning Bot

Этот проект представляет собой Telegram-бота для изучения иврита русскоговорящей аудиторией. Бот предоставляет различные функции для изучения новых слов, повторения выученных, участия в соревнованиях и управления базой данных.

## Структура проекта

Проект организован следующим образом:

Auxiliaries
    \n├── init.py
    \n├── commands.py # Команды бота
    \n├── helps.py # Вспомогательные функции
    \n├── states.py # Состояния FSM (Finite State Machine)
    \n├── texts.py # Тексты сообщений
Database
    ├── init.py
    ├── engine.py # Движок базы данных
    ├── models.py # Модели базы данных
    ├── orm_query.py # ORM-запросы
Handlers
    ├── init.py
    ├── competition.py # Обработчик соревнований
    ├── delete.py # Обработчик удаления данных
    ├── get_loggs.py # Обработчик получения логов
    ├── get_words.py # Обработчик получения слов
    ├── learn_general.py # Обработчик общего обучения
    ├── learn_personal.py # Обработчик персонального обучения
    ├── save_general.py # Обработчик сохранения общего прогресса
    ├── save_personal.py # Обработчик сохранения персонального прогресса
    ├── start.py # Обработчик команды старта
Loggs
    ├── init.py
    ├── logger_config.py # Конфигурация логгера
Middleware
    ├── init.py
    ├── middleware.py # Middleware для бота
.gitignore # Исключения для Git
main.py # Основной файл запуска бота


## Установка и запуск

### Требования

- Python 3.8 или выше
- Виртуальное окружение (рекомендуется)

### Установка

1. Склонируйте репозиторий:
    ```bash
    git clone https://github.com/Sa6e4ka/Hebrew-Bot.git
    ```

2. Перейдите в директорию проекта:
    ```bash
    cd Hebrew-Bot
    ```

3. Создайте и активируйте виртуальное окружение:
    ```bash
    python -m venv venv
    source venv/bin/activate  # На Windows: venv\Scripts\activate
    ```

4. Установите зависимости:
    ```bash
    pip install -r requirements.txt
    ```

5. Создайте файл `.env` в корневой директории проекта и добавьте следующие переменные:
    ```env
    TOKEN=<ваш_токен_бота>
    DATABASE_URL=<ваш_url_базы_данных>
    ```

### Запуск

Для запуска бота выполните следующую команду:
```bash
python main.py
