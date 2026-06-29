# Команды бота @ai_insiders_bot

## Общая логика
- Старт: приветствие + кнопки.
- Покупка: выбор способа оплаты → реквизиты из `prompts.json`.
- Вопросы: текст пересылается всем админам.

## Админ-команды
| Команда | Описание | Кто может |
|---------|----------|-----------|
| /start | Точка входа, показывает приветствие. | все |
| /stats | Статистика запусков, открытий курса, вопросов и способов оплаты. | админы |
| /addadmin <user_id\|@username> | Добавить нового админа. | админы |
| /setwelcome | Изменить приветственный текст (/start). Бот попросит прислать новый текст. | админы |

## Режимы работы
- **Webhook** (по умолчанию на Render): Telegram сам отправляет сообщения на сервер. Гарантированная доставка, 24/7.
- **Long polling** (локально): бот сам поллит Telegram.

## Репозиторий
- GitHub: https://github.com/workreplit3-ctrl/ai_insiders_bot

## Расположение файлов
- Конфиг: `config.py`
- Приветствие и реквизиты: `prompts.json`
- Бот: `bot_improved.py`

## Развёртывание на Render
1. Зайди на render.com
2. New → Web Service
3. Подключи репозиторий `workreplit3-ctrl/ai_insiders_bot`
4. Render сам подтянет `render.yaml`
5. Укажи переменные окружения:
   - `BOT_TOKEN` — токен от @BotFather
   - `ADMIN_IDS` — ID админов через запятую (например: `7085470065`)
   - `TELEGRAM_WEBHOOK_URL` — адрес сервиса Render (напр. `https://ai-insiders-bot.onrender.com`)
   - `TELEGRAM_WEBHOOK_SECRET` — любой случайный секрет
6. Нажми **Create Web Service**

После деплоя проверить в логах строчку:
`Webhook установлен: https://ai-insiders-bot.onrender.com/webhook`
