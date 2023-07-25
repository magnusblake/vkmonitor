# VKMonitor — небольшой мониторинг сообществ VK

## Описание

VKMonitor — это небольшой асинхронный бот, написанный на Python, который использует API VK для мониторинга заданных сообществ и Telegram API для отправки отчётов со статистикой в чат Telegram. 

VKMonitor собирает информацию о количестве новых постов, подсчитывает новых подписчиков, охват, а также рекламные посты. Бот перезапускает мониторинг и собирает статистику каждый день в указанное в конфигурации время.

Вместе с каждым отчетом VKMonitor также отправляет изображение, связанное с сообществом в конфигурационном файле.

## Требования

- Python 3.7 или выше
- aiohttp
- asyncio
- aiosqlite
- aiogram
- babel

## Установка

1. Клонируйте репозиторий:
    ```
    git clone https://github.com/noleeq/vkmonitor.git
    ```

2. Перейдите в директорию проекта:
    ```
    cd vkmonitor
    ```

3. Установите зависимости:
    ```
    pip install -r requirements.txt
    ```
    
## Конфигурация

Для настройки бота отредактируйте файл `config.py`:

1. **Основные настройки**
    - `telegramToken`: Токен вашего бота в Telegram.
    - `telegramChatID`: ID чата в Telegram, куда будут отправляться отчеты.
    - `vkToken`: Токен вашего приложения в VK.
    - `vkGroupsID`: Список ID сообществ VK, которые нужно мониторить.
    - `webPagePreview`: Включает или отключает предпросмотр веб-страниц в отчётах (например True или False).
    - `specialChar`: Специальный символ, используемый в публикациях с прямой рекламой.
    - `appLocale`: Язык локализации времени (например, "ru" для русского).

2. **Настройки API**
    - `vkAPIUrl`: URL-адрес API VK.
    - `vkAPIVersion`: Версия API VK, которую вы используете.

3. **Настройки изображений**
    - `imageStart`: Путь к изображению, которое отправляется при запуске мониторинга.
    - `imageStop`: Путь к изображению, которое отправляется при остановке мониторинга.
    - `imagesGroup`: Словарь, где ключи — это ID сообществ, а значения — это пути к соответствующим изображениям.

4. **Настройки базы данных**
    - `databaseName`: Имя файла базы данных.

5. **Настройки времени**
    - `timeHours`: Часы, в которые будет отправляться отчёт.
    - `timeMinutes`: Минуты, в которые будет отправляться отчёт.

6. **Настройки текста**
    - `captionImageStart`: Текстовое сообщение, которое отправляется при запуске мониторинга.
    - `captionImageStop`: Текстовое сообщение, которое отправляется при остановке мониторинга.

После внесения изменений сохраните и закройте файл. 

## Запуск

Чтобы запустить бота, используйте следующую команду:

```
python main.py
```

## Лицензия

Этот проект лицензирован под лицензией MIT. Подробности смотрите в файле `LICENSE`.
