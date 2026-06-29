# AI Insiders Bot

Клон @ai_insiders_bot — Telegram-бот для мастер-класса по AI-агентам.

## Функционал
- Приветствие и кнопки меню
- Выбор способа оплаты (Sber, PayPal, Revolut, Crypto)
- Сбор вопросов пользователей
- Админ-панель: статистика, добавление админов, смена приветствия

## Технологии
- Python 3.11
- aiogram 3.x
- Развёртывание: Render

## Локальный запуск
```bash
git clone https://github.com/workreplit3-ctrl/ai_insiders_bot.git
cd ai_insiders_bot
python -m venv .venv
source .venv/Scripts/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python bot_improved.py
```

## Развёртывание на Render
1. Создай аккаунт на render.com
2. New → Web Service
3. Подключи репозиторий `workreplit3-ctrl/ai_insiders_bot`
4. Укажи переменные окружения:
   - `BOT_TOKEN` — токен от @BotFather
   - `ADMIN_IDS` — ID админов через запятую (например: `7085470065`)

Бот будет работать 24/7.
