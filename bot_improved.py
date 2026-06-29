import asyncio
import json
import logging
import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from aiogram import Bot, Dispatcher, F
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardRemove,
)
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

import config
from prompts import get_welcome_prompt, get_payment_message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROMPTS_PATH = Path("prompts.json")
STATS_PATH = Path("stats.json")

dp = Dispatcher(storage=MemoryStorage())


class WelcomeState(StatesGroup):
    waiting_for_text = State()


# ---------------- Stats ----------------


def load_stats() -> dict:
    if not STATS_PATH.exists():
        return {
            "started": 0,
            "course_views": 0,
            "questions_asked": 0,
            "payments_viewed": defaultdict(int),
        }
    with STATS_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    data["payments_viewed"] = defaultdict(int, data.get("payments_viewed", {}))
    return data


def save_stats(stats: dict):
    out = dict(stats)
    out["payments_viewed"] = dict(out.get("payments_viewed", {}))
    with STATS_PATH.open("w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)


def update_stats(key: str, value: int = 1):
    stats = load_stats()
    if key == "payment_viewed":
        method = value
        stats["payments_viewed"][method] = stats.get("payments_viewed", {}).get(method, 0) + 1
    else:
        stats[key] = stats.get(key, 0) + 1
    save_stats(stats)


# ---------------- Keyboards ----------------


def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="💳 Купить курс", callback_data="buy_course"),
            ],
            [
                InlineKeyboardButton(text="❓ Задать вопрос", callback_data="ask_question"),
            ],
        ]
    )


def payment_methods_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🏦 Sber", callback_data="pay:sber"),
                InlineKeyboardButton(text="🌐 PayPal", callback_data="pay:paypal"),
            ],
            [
                InlineKeyboardButton(text="🏧 Revolut", callback_data="pay:revolut"),
                InlineKeyboardButton(
                    text="₿ Crypto", callback_data="pay:crypto"
                ),
            ],
            [
                InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu"),
            ],
        ]
    )


def back_to_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⬅️ В главное меню", callback_data="main_menu"),
            ]
        ]
    )


# ---------------- Handlers ----------------


@dp.message(CommandStart())
async def cmd_start(message: Message):
    if not config.BOT_TOKEN:
        await message.answer("❌ Ошибка: токен бота не настроен.")
        return

    user = message.from_user
    if config.ADMIN_IDS and user.id in config.ADMIN_IDS:
        await message.answer(
            "Вы администратор этого бота.\nИспользуйте:\n/stats — статистика\n/addadmin <user_id|@username> — добавить админа",
            reply_markup=main_menu_keyboard(),
        )
    else:
        text = get_welcome_prompt()
        await message.answer(text, reply_markup=main_menu_keyboard())

    update_stats("started")


@dp.callback_query(F.data == "main_menu")
async def main_menu(callback: CallbackQuery):
    text = get_welcome_prompt()
    await callback.message.edit_text(text, reply_markup=main_menu_keyboard())
    await callback.answer()


@dp.callback_query(F.data == "buy_course")
async def buy_course_handler(callback: CallbackQuery):
    text = "Выберите способ оплаты:"
    await callback.message.edit_text(text, reply_markup=payment_methods_keyboard())
    update_stats("course_views")
    await callback.answer()


@dp.callback_query(F.data.startswith("pay:"))
async def payment_details(callback: CallbackQuery):
    method = callback.data.split(":")[1]
    text = get_payment_message(method)
    update_stats("payment_viewed", method)
    await callback.message.edit_text(text, reply_markup=back_to_main_keyboard())
    await callback.answer()


@dp.callback_query(F.data == "ask_question")
async def ask_question_handler(callback: CallbackQuery):
    await callback.message.edit_text(
        "Напишите ваш вопрос одним сообщением. Мы ответим как можно скорее.",
        reply_markup=back_to_main_keyboard(),
    )
    await callback.answer()


@dp.message(F.text & ~F.text.startswith("/"))
async def collect_question(message: Message):
    # Simple question flow: any text after 'ask_question' is treated as a question
    text = message.text.strip()
    if len(text) < 3:
        await message.answer("Вопрос слишком короткий. Опишите подробнее.")
        return

    user = message.from_user
    q_text = f"Новый вопрос от @{user.username or user.id}:\n\n{text}"
    for admin_id in config.ADMIN_IDS:
        try:
            await message.bot.send_message(admin_id, q_text)
        except Exception as e:
            logger.warning(f"Не удалось отправить вопрос админу {admin_id}: {e}")

    await message.answer(
        "✅ Вопрос отправлен. Мы свяжемся с вами в ближайшее время.",
        reply_markup=ReplyKeyboardRemove(),
    )
    update_stats("questions_asked")


# ---------------- Admin commands ----------------


@dp.message(Command("stats"))
async def admin_stats(message: Message):
    if config.ADMIN_IDS and message.from_user.id not in config.ADMIN_IDS:
        await message.answer("⛔ Нет доступа.")
        return

    stats = load_stats()
    payments = stats.get("payments_viewed", {})
    pay_lines = "\n".join(f"- {k}: {v}" for k, v in payments.items()) or "Пока нет"

    text = (
        f"📊 Статистика бота:\n\n"
        f"Запустили бота: {stats.get('started', 0)}\n"
        f"Открыли курс: {stats.get('course_views', 0)}\n"
        f"Задано вопросов: {stats.get('questions_asked', 0)}\n\n"
        f"Оплаты (по методам):\n{pay_lines}\n"
    )
    await message.answer(text)


@dp.message(Command("addadmin"))
async def add_admin(message: Message):
    if config.ADMIN_IDS and message.from_user.id not in config.ADMIN_IDS:
        await message.answer("⛔ Нет доступа.")
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        await message.answer("Использование: /addadmin <user_id|@username>")
        return

    raw = parts[1].strip()
    new_admin_id = None

    if raw.startswith("@"):
        username = raw.lstrip("@")
        # Try to resolve username from recent updates via getChat
        try:
            chat = await message.bot.get_chat(username)
            new_admin_id = chat.id
        except Exception as e:
            await message.answer(
                f"Не удалось найти пользователя {raw}. Убедитесь, что он когда-либо писал боту.\nОшибка: {e}"
            )
            return
    else:
        try:
            new_admin_id = int(raw)
        except ValueError:
            await message.answer("user_id должен быть числом.")
            return

    if new_admin_id in config.ADMIN_IDS:
        await message.answer("Этот пользователь уже админ.")
        return

    config.ADMIN_IDS.append(new_admin_id)

    await message.answer(f"✅ Добавлен админ: {new_admin_id}")
    try:
        await message.bot.send_message(
            new_admin_id, "Вам предоставлены права администратора в боте."
        )
    except Exception as e:
        logger.info(f"Не удалось уведомить нового админа: {e}")


@dp.message(Command("setwelcome"))
async def set_welcome_start(message: Message, state: FSMContext):
    if config.ADMIN_IDS and message.from_user.id not in config.ADMIN_IDS:
        await message.answer("⛔ Нет доступа.")
        return
    await state.set_state(WelcomeState.waiting_for_text)
    await message.answer("Отправьте новый приветственный текст для бота:")


@dp.message(WelcomeState.waiting_for_text)
async def set_welcome_save(message: Message, state: FSMContext):
    from prompts import save_welcome_prompt

    new_text = message.text.strip()
    save_welcome_prompt(new_text)
    await state.clear()
    await message.answer("✅ Приветственный текст обновлён.")


# ---------------- Main ----------------


async def main():
    http_proxy = os.getenv("HTTP_PROXY") or os.getenv("HTTPS_PROXY")
    if http_proxy:
        session = AiohttpSession(proxy=http_proxy)
        bot = Bot(token=config.BOT_TOKEN, session=session)
    else:
        bot = Bot(token=config.BOT_TOKEN)

    logger.info("Запуск бота...")
    try:
        await dp.start_polling(bot, skip_updates=True)
    finally:
        if http_proxy:
            await session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен.")
