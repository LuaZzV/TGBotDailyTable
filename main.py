from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackContext,
    JobQueue,
)
import datetime
import logging

logging.basicConfig(level=logging.INFO)

# Токен вашего бота
BOT_TOKEN = "8422722132:AAHw0ORNqRc1BxaiEgHc6yfaJ7luGuSJD80"
# ID группы или темы, куда отправлять сообщения (должен начинаться с - для групп)
CHAT_ID = -2988199928

# Пример расписания по дням недели (0 - понедельник, 6 - воскресенье)
schedule = {
    0: "Понедельник:\n8:00 - 9:30 Физ-ра (Лекция) 318\n9:40 - 11:10 (1)Физика (Лекция), (2)Математика (Лекция) 318\n11:10 - 12:50 (1)История (Лекция) 318, (2)ИИКГ (Лекция) 318",
    1: "Вторник:\n11:20 - 12:50 (1)Физ-ра (Практика), (2)Физ-ра (Лекция) 404В\n14:50 - 18:00 (1)(2)ИЯ (Практика) 217",
    2: "Среда:\n9:40 - 11:10 История (Лекция) 354\n11:20 - 12:50 ДКИРЯ (Лекция) 354",
    3: "Четверг:\n8:00 - 11:10 (1)(2)ИИКГ (Практика) 121В\n11:20 - 12:50 Математика (Практика) 504В\n13:10 - 16:20 (1)(2)Физика (Практика)",
    4: "Пятница:\n11:20 - 12:50 ДКИРЯ (Практика) 318\n13:10 - 14:40 История (Практика) 436\n14:50 - 16:20 Физ-ра (Практика)",
    5: "Суббота:\nВыходной",
    6: "Воскресенье:\nВыходной",
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Команды:\n"
        "/schedule - показать расписание на сегодня\n"
        "/setschedule <день недели> <текст> - изменить расписание\n"
        "День недели: 0 - понедельник, 6 - воскресенье."
    )

async def show_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = datetime.datetime.now().weekday()
    text = schedule.get(today, "Расписание отсутствует на сегодня.")
    await update.message.reply_text(f"Расписание на сегодня:\n{text}")

async def set_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        day = int(context.args[0])
        if day < 0 or day > 6:
            await update.message.reply_text("Ошибка: день недели должен быть в диапазоне 0..6.")
            return
    except (IndexError, ValueError):
        await update.message.reply_text("Использование: /setschedule <день недели> <текст>")
        return

    text = " ".join(context.args[1:])
    if not text:
        await update.message.reply_text("Ошибка: необходимо указать текст расписания.")
        return

    schedule[day] = text
    await update.message.reply_text(f"Расписание для дня {day} обновлено.")

async def send_daily_schedule(context: CallbackContext):
    today = datetime.datetime.now().weekday()
    text = schedule.get(today, "Расписание отсутствует на сегодня.")
    await context.bot.send_message(chat_id=CHAT_ID, text=f"Расписание на сегодня:\n{text}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("schedule", show_schedule))
    app.add_handler(CommandHandler("setschedule", set_schedule))

    # Запускаем Job для ежедневной отправки в 8:00
    job_queue = app.job_queue
    time_to_send = datetime.time(hour=8, minute=0, second=0)
    job_queue.run_daily(send_daily_schedule, time_to_send)

    app.run_polling()

if __name__ == "__main__":
    main()
