# Hebrew Learning Bot

Этот проект представляет собой Telegram-бота для отложенного постинга видео в канал telegram с параллельной потоковой их загрузкой на бакет aws s3

## Установка и запуск

### Требования

- Python 3.8 или выше
- Виртуальное окружение (рекомендуется)

### Установка

1. Склонируйте репозиторий:

   ```bash
   git clone https://github.com/Sa6e4ka/DTB_post.git
   ```

2. Перейдите в директорию проекта:

   ```bash
   cd DTB_post
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
    AWS_ACCESS_KEY=...
    AWS_SECRET_KEY=...
    AWS_BUCKET_NAME=...

    TOKEN=<ваш_токен_бота>
    CHANNEL_ID=...
   ```

### Запуск

Для запуска бота выполните следующую команду:

```bash
python main.py
```
