import json
from pathlib import Path
from typing import List

PROMPTS_PATH = Path("prompts.json")


def load_prompts() -> dict:
    if not PROMPTS_PATH.exists():
        return {}
    with PROMPTS_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_prompts(prompts: dict):
    with PROMPTS_PATH.open("w", encoding="utf-8") as f:
        json.dump(prompts, f, ensure_ascii=False, indent=2)


WELCOME_PROMPT_FALLBACK = "Добро пожаловать в мой Бот!\nПровожу мастер-класс по AI-агентам.\nС нуля покажу, как собрать свою AI-команду, даже если ты совсем новичок и не технарь.\nЖми ниже кнопку \"Купить курс\" - расскажу что внутри и как забрать место"


def get_welcome_prompt(language: str = "ru") -> str:
    prompts = load_prompts()
    return prompts.get("welcome_prompt", WELCOME_PROMPT_FALLBACK)


def get_payment_message(payment_type: str) -> str:
    prompts = load_prompts()
    return prompts.get("payment_details", {}).get(payment_type, "Реквизиты временно отсутствуют.")


def save_welcome_prompt(text: str):
    prompts = load_prompts()
    prompts["welcome_prompt"] = text
    save_prompts(prompts)
