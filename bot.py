import os
import random
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes,
)

TOKEN = "8935008936:AAGhQ54A9TwfIjVqie712laYxk_JHghHLKE"

PROFILE, ILLUSION, PATH, METHOD, VISUALIZATION_CHOICE = range(5)
user_arcanes = {}

ARCANE_TEXTS = {}

# ---------- ВСТАВЬТЕ ВАШИ ПОЛНЫЕ ТЕКСТЫ АРКАНОВ (0..21) ----------
# Здесь должны быть все ваши арканы с profile, illusion, path, method, visualization.
# Для примера оставлена заглушка. Вы замените её на свои тексты.
for i in range(22):
    ARCANE_TEXTS[i] = {
        "profile": f"Профиль аркана {i} (замените на свой)",
        "illusion": f"Иллюзия аркана {i}",
        "path": f"Путь аркана {i}",
        "method": f"Методика аркана {i}",
        "visualization": f"Визуализация аркана {i}",
    }
# ---------- ЗАМЕНИТЕ ЗАГЛУШКИ НА ВАШИ 22 АРКАНА ----------

def get_random_arcane(exclude_list):
    available = [a for a in range(22) if a not in exclude_list]
    return random.choice(available) if available else None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_arcanes[user_id] = []
    context.user_data["step"] = PROFILE
    keyboard = [[KeyboardButton("🌿 Начать исследование")]]
    await update.message.reply_text(
        "🎭 *«Арканы творческих состояний»*\n\nИгра-оракул для поиска вдохновения.\nНажми «Начать исследование».",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
    )
    return PROFILE

async def start_research(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton("🎴 Вытянуть карту")]]
    await update.message.reply_text(
        "🧿 *Шаг 1: Твой творческий профиль*\n\nНастройся и вытяни карту.",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
    )
    return PROFILE

async def draw_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    current_state = context.user_data.get("step", PROFILE)
    arcane = get_random_arcane(user_arcanes[user_id])
    if arcane is None:
        await update.message.reply_text("Все карты использованы! Напиши /start")
        return ConversationHandler.END
    user_arcanes[user_id].append(arcane)
    if current_state == PROFILE:
        text = ARCANE_TEXTS[arcane]["profile"]
        next_step = ILLUSION
        next_message = "🌀 *Шаг 2: Твоя иллюзия*\n\nВытяни карту."
    elif current_state == ILLUSION:
        text = ARCANE_TEXTS[arcane]["illusion"]
        next_step = PATH
        next_message = "🛤 *Шаг 3: Твой путь*\n\nВытяни карту."
    else:
        text = ARCANE_TEXTS[arcane]["path"]
        next_step = METHOD
        next_message = "📖 *Шаг 4: Твоя методика*\n\nНажми «Получить методику»."
    image_path = f"images/{arcane:02d}.jpeg"
    if os.path.exists(image_path):
        with open(image_path, "rb") as photo:
            await update.message.reply_photo(photo=photo)
            await update.message.reply_text(f"✨ *Карта*\n\n{text}", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"✨ *Карта*\n\n{text}", parse_mode="Markdown")
    if current_state == PATH:
        keyboard = [[KeyboardButton("📜 Получить методику")]]
        await update.message.reply_text(next_message, parse_mode="Markdown", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    else:
        keyboard = [[KeyboardButton("🎴 Вытянуть карту")]]
        await update.message.reply_text(next_message, parse_mode="Markdown", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    context.user_data["step"] = next_step
    return next_step

async def get_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    first_arcane = user_arcanes[user_id][0]
    await update.message.reply_text(f"🔮 *Твоя методика:*\n\n{ARCANE_TEXTS[first_arcane]['method']}", parse_mode="Markdown")
    keyboard = [[KeyboardButton("✨ Да, погрузиться"), KeyboardButton("⏳ Вернусь позже")]]
    await update.message.reply_text("🎧 *Готов ли ты погрузиться в образ?*", parse_mode="Markdown", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return VISUALIZATION_CHOICE

async def send_visualization(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    first_arcane = user_arcanes[user_id][0]
    await update.message.reply_text(f"🎧 *Визуализация*\n\n{ARCANE_TEXTS[first_arcane]['visualization']}", parse_mode="Markdown")
    book_image_path = "book_cover.jpg"
    caption = (
        "✨ *Игра завершена!*\n\n"
        "Ты готов(а) изменить мир своими идеями.\n"
        "Твоя уникальность неоспорима.\n\n"
        "📖 *Я написала книгу «Точка вдохновения», чтобы творить несмотря ни на что.*\n"
        "Она поможет создавать что угодно из твоей уникальности, подскажет, как перестать откладывать "
        "и станет точкой старта твоих идей.\n\n"
        "👉 [Переходи по ссылке](https://ridero.ru/books/tochka_vdokhnoveniya/)"
    )
    if os.path.exists(book_image_path):
        with open(book_image_path, "rb") as book_photo:
            await update.message.reply_photo(photo=book_photo, caption=caption, parse_mode="Markdown")
    else:
        await update.message.reply_text(caption, parse_mode="Markdown")
    keyboard = [[KeyboardButton("📝 Написать отзыв"), KeyboardButton("🙏 Благодарю"), KeyboardButton("📤 Поделиться")]]
    await update.message.reply_text("👇 Выберите действие:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return ConversationHandler.END

async def later_visualization(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton("🌀 Трансформирующий образ")]]
    await update.message.reply_text("Нажми, когда будешь готов.", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return VISUALIZATION_CHOICE

async def share(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_info = await context.bot.get_me()
    await update.message.reply_text(f"Поделись игрой: https://t.me/{bot_info.username}")

async def thanks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🙌 Спасибо за игру! Возвращайся.")

async def feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Напиши отзыв сюда, он придёт автору: @ksusha_slushai")

def main():
    app = Application.builder().token(TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            PROFILE: [
                MessageHandler(filters.Text("🌿 Начать исследование"), start_research),
                MessageHandler(filters.Text("🎴 Вытянуть карту"), draw_card),
            ],
            ILLUSION: [MessageHandler(filters.Text("🎴 Вытянуть карту"), draw_card)],
            PATH: [MessageHandler(filters.Text("🎴 Вытянуть карту"), draw_card)],
            METHOD: [MessageHandler(filters.Text("📜 Получить методику"), get_method)],
            VISUALIZATION_CHOICE: [
                MessageHandler(filters.Text("✨ Да, погрузиться"), send_visualization),
                MessageHandler(filters.Text("⏳ Вернусь позже"), later_visualization),
                MessageHandler(filters.Text("🌀 Трансформирующий образ"), send_visualization),
            ],
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
    )
    app.add_handler(conv)
    app.add_handler(MessageHandler(filters.Text("📝 Написать отзыв"), feedback))
    app.add_handler(MessageHandler(filters.Text("🙏 Благодарю"), thanks))
    app.add_handler(MessageHandler(filters.Text("📤 Поделиться"), share))

    # ЗАПУСК ЧЕРЕЗ ВЕБХУК
    port = int(os.environ.get("PORT", 8000))
    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=TOKEN,
        webhook_url=f"https://github.com/moeprizvaniye-afk/arcane_bot.git/{TOKEN}"   # ЗАМЕНИТЕ ваш-бот.bothost.ru
    )

if __name__ == "__main__":
    main()
