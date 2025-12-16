import random
import asyncio
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

QUEST_FILE = "quest.txt"
STATS_FILE = "stats.txt"

def load_questions():
    questions = []
    if not os.path.exists(QUEST_FILE):
        raise FileNotFoundError("questions.txt не найден")
    with open(QUEST_FILE, "r", encoding="utf-8") as f:
        block = []
        for line in f:
            line = line.strip()
            if line:
                block.append(line)
            else:
                if block:
                    questions.append(parse_block(block))
                    block = []
        if block:
            questions.append(parse_block(block))
    return questions

def parse_block(block):
    category = block[0][1:-1]
    question = block[1]
    options = []
    correct = ""
    for line in block[2:]:
        if line.startswith("*"):
            correct = line[1:]
            options.append(correct)
        else:
            options.append(line)
    random.shuffle(options)
    return {"category": category,"question": question,"options": options,"correct": correct}

QUESTIONS = load_questions()
user_state = {}

def load_stats():
    stats = {}
    if not os.path.exists(STATS_FILE):
        return stats
    with open(STATS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            uid, total, correct, cats = line.strip().split("|")
            categories = {}
            if cats:
                for c in cats.split(","):
                    k, v = c.split(":")
                    categories[k] = int(v)
            stats[uid] = {"total": int(total),"correct": int(correct),"categories": categories}
    return stats

def save_stats(stats):
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        for uid, s in stats.items():
            cats = ",".join(f"{k}:{v}" for k, v in s["categories"].items())
            f.write(f"{uid}|{s['total']}|{s['correct']}|{cats}\n")

stats_data = load_stats()

def init_user(uid):
    if uid not in stats_data:
        stats_data[uid] = {"total": 0,"correct": 0,"categories": {}}

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎯 Случайный вопрос", callback_data="random")],
        [InlineKeyboardButton("📚 Все вопросы подряд", callback_data="all")],
        [InlineKeyboardButton("📊 Статистика", callback_data="stats")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привет! Я квиз-бот\nВыбери режим:", reply_markup=main_menu())

async def start_quiz(query, mode):
    order = list(range(len(QUESTIONS)))
    if mode == "random":
        order = [random.choice(order)]
    else:
        random.shuffle(order)
    user_state[query.from_user.id] = {"order": order, "index": 0}
    await send_question(query)

async def send_question(query):
    state = user_state.get(query.from_user.id)
    if not state or state["index"] >= len(state["order"]):
        await query.message.reply_text("🎉 Готово!", reply_markup=main_menu())
        user_state.pop(query.from_user.id, None)
        return
    q = QUESTIONS[state["order"][state["index"]]]
    buttons = [[InlineKeyboardButton(opt, callback_data=f"ans:{i}")] for i, opt in enumerate(q["options"])]
    buttons.append([InlineKeyboardButton("⬅️ В меню", callback_data="menu")])
    await query.message.reply_text(f"📂 {q['category']}\n\n{q['question']}", reply_markup=InlineKeyboardMarkup(buttons))

async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = str(query.from_user.id)
    if query.data == "menu":
        user_state.pop(query.from_user.id, None)
        await query.message.reply_text("Вы вернулись в главное меню:", reply_markup=main_menu())
        return
    if query.data in ("random", "all"):
        await start_quiz(query, query.data)
        return
    if query.data == "stats":
        s = stats_data.get(uid)
        if not s:
            await query.message.reply_text("📭 Статистики нет")
            return
        best = max(s["categories"], key=s["categories"].get) if s["categories"] else "—"
        await query.message.reply_text(f"📊 Статистика:\nВсего: {s['total']}\nПравильных: {s['correct']}\nЛучшая тема: {best}")
        return
    if query.data.startswith("ans"):
        idx = int(query.data.split(":")[1])
        state = user_state[query.from_user.id]
        q = QUESTIONS[state["order"][state["index"]]]
        init_user(uid)
        stats_data[uid]["total"] += 1
        chosen = q["options"][idx]
        if chosen == q["correct"]:
            stats_data[uid]["correct"] += 1
            stats_data[uid]["categories"].setdefault(q["category"], 0)
            stats_data[uid]["categories"][q["category"]] += 1
            result = "Верно ✅"
        else:
            result = f"Неверно ❌\nПравильно: {q['correct']}"
        save_stats(stats_data)
        await query.edit_message_text(f"{q['question']}\n\nВаш ответ: {chosen}\n{result}")
        state["index"] += 1
        await asyncio.sleep(0.5)
        await send_question(query)

def main():
    app = ApplicationBuilder().token("8216640069:AAGSryXUbkj2PID0SNSrS-mKD-BurKMXcTg").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callbacks))
    app.run_polling()

if __name__ == "__main__":
    main()
