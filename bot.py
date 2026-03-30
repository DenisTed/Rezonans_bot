import json
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
    ReplyKeyboardMarkup
)
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

from config import TOKEN, WEB_APP_URL, ADMINS
from database import (
    init_db,
    add_user,
    get_all_users,
    add_ticket_order,
    get_last_orders,
    save_message
)

support_mode_users = set()


def is_admin(user_id: int) -> bool:
    return user_id in ADMINS


def get_user_keyboard():
    keyboard = [
        ["🎭 Відкрити театр", "💬 Написати адміну"],
        ["📞 Контакти", "ℹ️ Допомога"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    add_user(
        telegram_id=user.id,
        first_name=user.first_name or "",
        username=user.username or ""
    )

    await update.message.reply_text(
        f"Вітаємо, {user.first_name}!\n\n"
        f"Це бот театру “Резонанс”.\n"
        f"Оберіть дію кнопками нижче.",
        reply_markup=get_user_keyboard()
    )


async def open_theatre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎭 Відкрити інтерфейс театру", web_app=WebAppInfo(url=WEB_APP_URL))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Натисніть кнопку нижче, щоб відкрити інтерфейс театру:",
        reply_markup=reply_markup
    )


async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    support_mode_users.add(user_id)

    await update.message.reply_text(
        "Напишіть повідомлення адміністратору.\n"
        "Щоб вийти з цього режиму, натисніть /cancel"
    )


async def contacts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📞 Контакти театру “Резонанс”:\n\n"
        "Адреса: м. Кропивницький, вул. Театральна, 12\n"
        "Телефон: +38 (050) 123-45-67\n"
        "Email: rezonans.theatre@gmail.com"
    )


async def help_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ Що можна зробити:\n\n"
        "🎭 Відкрити театр — переглянути афішу, прем’єри, квитки\n"
        "💬 Написати адміну — поставити питання живій людині\n"
        "📞 Контакти — переглянути контакти театру"
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    support_mode_users.discard(user_id)

    await update.message.reply_text(
        "Режим звернення до адміністратора вимкнено.",
        reply_markup=get_user_keyboard()
    )


async def users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    users = get_all_users()

    if not users:
        await update.message.reply_text("Користувачів ще немає.")
        return

    text = "👥 Список користувачів:\n\n"
    for tg_id, first_name, username, registered_at in users[:20]:
        text += (
            f"ID: {tg_id}\n"
            f"Ім’я: {first_name}\n"
            f"Username: @{username if username else 'немає'}\n"
            f"Реєстрація: {registered_at[:19]}\n\n"
        )

    await update.message.reply_text(text)


async def orders_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    orders = get_last_orders()

    if not orders:
        await update.message.reply_text("Заявок ще немає.")
        return

    text = "🎟 Останні заявки:\n\n"
    for tg_id, name, show_name, ticket_count, comment, created_at, status in orders:
        text += (
            f"Користувач ID: {tg_id}\n"
            f"Ім’я: {name}\n"
            f"Вистава: {show_name}\n"
            f"Квитків: {ticket_count}\n"
            f"Коментар: {comment if comment else 'немає'}\n"
            f"Дата: {created_at[:19]}\n"
            f"Статус: {status}\n\n"
        )

    await update.message.reply_text(text)


async def reply_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    if len(context.args) < 2:
        await update.message.reply_text("Формат: /reply user_id текст")
        return

    try:
        user_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("user_id має бути числом.")
        return

    text = " ".join(context.args[1:])

    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"💬 Повідомлення від адміністратора:\n\n{text}"
        )
        save_message(user_id, 1, text)
        await update.message.reply_text("Відповідь надіслано.")
    except Exception as e:
        await update.message.reply_text(f"Не вдалося надіслати повідомлення: {e}")


async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    if not context.args:
        await update.message.reply_text("Формат: /broadcast текст повідомлення")
        return

    text = " ".join(context.args)
    users = get_all_users()

    sent = 0
    failed = 0

    for tg_id, _, _, _ in users:
        try:
            await context.bot.send_message(
                chat_id=tg_id,
                text=f"🎭 Новина від театру “Резонанс”:\n\n{text}"
            )
            sent += 1
        except Exception:
            failed += 1

    await update.message.reply_text(
        f"Розсилку завершено.\nУспішно: {sent}\nНе вдалося: {failed}"
    )


async def handle_webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw_data = update.message.web_app_data.data
    user = update.effective_user

    try:
        data = json.loads(raw_data)
        action = data.get("action")

        if action == "ticket_request":
            name = data.get("name", "")
            show = data.get("show", "")
            count = data.get("count", "")
            comment = data.get("comment", "")

            add_ticket_order(user.id, name, show, count, comment)

            await update.message.reply_text("✅ Вашу заявку прийнято. Адміністратор зв’яжеться з вами тут у боті.")

            admin_text = (
                f"🎟 Нова заявка на квитки\n\n"
                f"User ID: {user.id}\n"
                f"Ім’я: {name}\n"
                f"Вистава: {show}\n"
                f"Кількість: {count}\n"
                f"Коментар: {comment if comment else 'немає'}"
            )

            for admin_id in ADMINS:
                await context.bot.send_message(chat_id=admin_id, text=admin_text)

    except Exception as e:
        await update.message.reply_text(f"Помилка обробки даних: {e}")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text

    if is_admin(user.id):
        return

    if text == "🎭 Відкрити театр":
        await open_theatre(update, context)
        return

    if text == "💬 Написати адміну":
        await support(update, context)
        return

    if text == "📞 Контакти":
        await contacts(update, context)
        return

    if text == "ℹ️ Допомога":
        await help_text(update, context)
        return

    if user.id in support_mode_users:
        save_message(user.id, 0, text)

        admin_text = (
            f"📩 Нове повідомлення адміністратору\n\n"
            f"User ID: {user.id}\n"
            f"Ім’я: {user.first_name}\n"
            f"Username: @{user.username if user.username else 'немає'}\n"
            f"Текст: {text}\n\n"
            f"Щоб відповісти:\n"
            f"/reply {user.id} ваша відповідь"
        )

        for admin_id in ADMINS:
            await context.bot.send_message(chat_id=admin_id, text=admin_text)

        await update.message.reply_text("Ваше повідомлення передано адміністратору.")
        return

    await update.message.reply_text(
        "Оберіть дію кнопками нижче.",
        reply_markup=get_user_keyboard()
    )


def main():
    init_db()

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", cancel))

    # команди тільки для адміна
    app.add_handler(CommandHandler("users", users_command))
    app.add_handler(CommandHandler("orders", orders_command))
    app.add_handler(CommandHandler("reply", reply_command))
    app.add_handler(CommandHandler("broadcast", broadcast_command))

    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_webapp_data))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("Бот запущено...")
    app.run_polling()


if __name__ == "__main__":
    main()