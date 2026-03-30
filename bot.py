from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    ConversationHandler
)

from config import TOKEN, ADMINS
from database import (
    init_db,
    add_user,
    update_user_phone,
    get_user,
    get_all_users,
    add_show,
    get_active_shows,
    add_ticket_order,
    get_last_orders,
    get_user_orders,
    update_order_status,
    get_order_by_id
)

REGISTER_PHONE = 1
SUPPORT_MESSAGE = 2
ORDER_NAME = 10
ORDER_PHONE = 11
ORDER_SHOW = 12
ORDER_COUNT = 13
ORDER_COMMENT = 14


def is_admin(user_id: int) -> bool:
    return user_id in ADMINS


def get_user_keyboard():
    keyboard = [
        ["Зареєструватися", "Замовити квиток"],
        ["Мої квитки", "Актуальні вистави"],
        ["Написати адміну", "Контакти"],
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


# ---------------- REGISTRATION ----------------

async def register_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Введіть ваш номер телефону для реєстрації:",
        reply_markup=ReplyKeyboardRemove()
    )
    return REGISTER_PHONE


async def register_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text.strip()
    user_id = update.effective_user.id

    update_user_phone(user_id, phone)

    await update.message.reply_text(
        "Реєстрацію завершено.",
        reply_markup=get_user_keyboard()
    )
    return ConversationHandler.END


# ---------------- SHOWS ----------------

async def shows_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    shows = get_active_shows()

    if not shows:
        await update.message.reply_text("Зараз активних вистав немає.")
        return

    text = "Актуальні вистави:\n\n"
    for show_id, title, show_date, show_time, description in shows:
        text += (
            f"#{show_id} {title}\n"
            f"Дата: {show_date}\n"
            f"Час: {show_time}\n"
            f"Опис: {description if description else 'немає'}\n\n"
        )

    await update.message.reply_text(text)


# ---------------- MY TICKETS ----------------

async def my_tickets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    orders = get_user_orders(user_id)

    if not orders:
        await update.message.reply_text("У вас поки немає замовлень.")
        return

    text = "Ваші квитки:\n\n"
    for order_id, show_name, ticket_count, comment, created_at, status in orders:
        text += (
            f"Заявка №{order_id}\n"
            f"Вистава: {show_name}\n"
            f"Кількість: {ticket_count}\n"
            f"Коментар: {comment if comment else 'немає'}\n"
            f"Дата: {created_at[:19]}\n"
            f"Статус: {status}\n\n"
        )

    await update.message.reply_text(text)


# ---------------- ORDER TICKET ----------------

async def order_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Введіть ваше ім’я для замовлення квитка:",
        reply_markup=ReplyKeyboardRemove()
    )
    return ORDER_NAME


async def order_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["order_name"] = update.message.text.strip()
    await update.message.reply_text("Введіть ваш телефон:")
    return ORDER_PHONE


async def order_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["order_phone"] = update.message.text.strip()

    shows = get_active_shows()
    if not shows:
        await update.message.reply_text(
            "На жаль, зараз немає активних вистав.",
            reply_markup=get_user_keyboard()
        )
        return ConversationHandler.END

    keyboard = [[show[1]] for show in shows]
    keyboard.append(["Скасувати"])

    await update.message.reply_text(
        "Оберіть виставу:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return ORDER_SHOW


async def order_show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text == "Скасувати":
        await update.message.reply_text(
            "Замовлення скасовано.",
            reply_markup=get_user_keyboard()
        )
        return ConversationHandler.END

    context.user_data["show_name"] = text

    keyboard = [["1", "2", "3"], ["4", "5"], ["Скасувати"]]
    await update.message.reply_text(
        "Оберіть кількість квитків:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return ORDER_COUNT


async def order_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text == "Скасувати":
        await update.message.reply_text(
            "Замовлення скасовано.",
            reply_markup=get_user_keyboard()
        )
        return ConversationHandler.END

    context.user_data["ticket_count"] = text

    await update.message.reply_text(
        "Введіть коментар або напишіть '-' якщо без коментаря:",
        reply_markup=ReplyKeyboardRemove()
    )
    return ORDER_COMMENT


async def order_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    comment = update.message.text.strip()
    if comment == "-":
        comment = ""

    user = update.effective_user

    order_id = add_ticket_order(
        telegram_id=user.id,
        customer_name=context.user_data["order_name"],
        phone=context.user_data["order_phone"],
        show_name=context.user_data["show_name"],
        ticket_count=context.user_data["ticket_count"],
        comment=comment
    )

    await update.message.reply_text(
        f"Вашу заявку №{order_id} прийнято.\n"
        f"Статус: new",
        reply_markup=get_user_keyboard()
    )

    admin_text = (
        f"Нова заявка на квитки\n\n"
        f"Заявка №{order_id}\n"
        f"User ID: {user.id}\n"
        f"Ім’я: {context.user_data['order_name']}\n"
        f"Телефон: {context.user_data['order_phone']}\n"
        f"Вистава: {context.user_data['show_name']}\n"
        f"Кількість: {context.user_data['ticket_count']}\n"
        f"Коментар: {comment if comment else 'немає'}\n"
        f"Статус: new"
    )

    for admin_id in ADMINS:
        await context.bot.send_message(chat_id=admin_id, text=admin_text)

    context.user_data.clear()
    return ConversationHandler.END


# ---------------- SUPPORT ----------------

async def support_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Напишіть повідомлення адміністратору:",
        reply_markup=ReplyKeyboardRemove()
    )
    return SUPPORT_MESSAGE


async def support_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text.strip()

    admin_text = (
        f"Нове повідомлення адміністратору\n\n"
        f"User ID: {user.id}\n"
        f"Ім’я: {user.first_name}\n"
        f"Username: @{user.username if user.username else 'немає'}\n"
        f"Текст: {text}\n\n"
        f"Щоб відповісти:\n"
        f"/reply {user.id} ваша відповідь"
    )

    for admin_id in ADMINS:
        await context.bot.send_message(chat_id=admin_id, text=admin_text)

    await update.message.reply_text(
        "Ваше повідомлення передано адміністратору.",
        reply_markup=get_user_keyboard()
    )
    return ConversationHandler.END


# ---------------- INFO ----------------

async def contacts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Контакти театру “Резонанс”:\n\n"
        "Адреса: м. Кропивницький, вул. Театральна, 12\n"
        "Телефон: +38 (050) 123-45-67\n"
        "Email: rezonans.theatre@gmail.com"
    )


# ---------------- ADMIN ----------------

async def users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    users = get_all_users()
    if not users:
        await update.message.reply_text("Користувачів ще немає.")
        return

    text = "Список користувачів:\n\n"
    for tg_id, first_name, username, phone, registered_at in users[:20]:
        text += (
            f"ID: {tg_id}\n"
            f"Ім’я: {first_name}\n"
            f"Username: @{username if username else 'немає'}\n"
            f"Телефон: {phone if phone else 'немає'}\n"
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

    text = "Останні заявки:\n\n"
    for order_id, tg_id, customer_name, phone, show_name, ticket_count, comment, created_at, status in orders:
        text += (
            f"Заявка №{order_id}\n"
            f"User ID: {tg_id}\n"
            f"Ім’я: {customer_name}\n"
            f"Телефон: {phone}\n"
            f"Вистава: {show_name}\n"
            f"Квитків: {ticket_count}\n"
            f"Коментар: {comment if comment else 'немає'}\n"
            f"Дата: {created_at[:19]}\n"
            f"Статус: {status}\n\n"
        )

    await update.message.reply_text(text)


async def addshow_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    raw = " ".join(context.args)
    parts = [p.strip() for p in raw.split("|")]

    if len(parts) < 3:
        await update.message.reply_text(
            "Формат:\n"
            "/addshow Назва | Дата | Час | Опис"
        )
        return

    title = parts[0]
    show_date = parts[1]
    show_time = parts[2]
    description = parts[3] if len(parts) > 3 else ""

    add_show(title, show_date, show_time, description)
    await update.message.reply_text(f"Виставу '{title}' додано.")


async def confirm_order_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    if len(context.args) != 1:
        await update.message.reply_text("Формат: /confirm_order order_id")
        return

    order_id = int(context.args[0])
    order = get_order_by_id(order_id)

    if not order:
        await update.message.reply_text("Заявку не знайдено.")
        return

    update_order_status(order_id, "confirmed")
    _, user_id, customer_name, _, show_name, ticket_count, _, _, _ = order

    await update.message.reply_text(f"Заявка №{order_id} підтверджена.")

    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                f"Вашу заявку №{order_id} підтверджено.\n"
                f"Вистава: {show_name}\n"
                f"Кількість квитків: {ticket_count}\n"
                f"Глядач: {customer_name}"
            )
        )
    except Exception:
        pass


async def cancel_order_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    if len(context.args) != 1:
        await update.message.reply_text("Формат: /cancel_order order_id")
        return

    order_id = int(context.args[0])
    order = get_order_by_id(order_id)

    if not order:
        await update.message.reply_text("Заявку не знайдено.")
        return

    update_order_status(order_id, "canceled")
    _, user_id, customer_name, _, show_name, ticket_count, _, _, _ = order

    await update.message.reply_text(f"Заявка №{order_id} скасована.")

    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                f"Вашу заявку №{order_id} скасовано.\n"
                f"Вистава: {show_name}\n"
                f"Кількість квитків: {ticket_count}\n"
                f"Глядач: {customer_name}"
            )
        )
    except Exception:
        pass


async def reply_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    if len(context.args) < 2:
        await update.message.reply_text("Формат: /reply user_id текст")
        return

    user_id = int(context.args[0])
    text = " ".join(context.args[1:])

    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"Повідомлення від адміністратора:\n\n{text}"
        )
        await update.message.reply_text("Відповідь надіслано.")
    except Exception as e:
        await update.message.reply_text(f"Помилка: {e}")


async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    if not context.args:
        await update.message.reply_text("Формат: /broadcast текст")
        return

    text = " ".join(context.args)
    users = get_all_users()

    sent = 0
    failed = 0

    for tg_id, _, _, _, _ in users:
        try:
            await context.bot.send_message(
                chat_id=tg_id,
                text=f"Новина від театру “Резонанс”:\n\n{text}"
            )
            sent += 1
        except Exception:
            failed += 1

    await update.message.reply_text(
        f"Розсилку завершено.\nУспішно: {sent}\nНе вдалося: {failed}"
    )


# ---------------- FALLBACK ----------------

async def fallback_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()

    if text == "Зареєструватися":
        return await register_start(update, context)

    if text == "Замовити квиток":
        return await order_start(update, context)

    if text == "Мої квитки":
        return await my_tickets(update, context)

    if text == "Актуальні вистави":
        return await shows_command(update, context)

    if text == "Написати адміну":
        return await support_start(update, context)

    if text == "Контакти":
        return await contacts(update, context)

    await update.message.reply_text(
        "Оберіть дію кнопками нижче.",
        reply_markup=get_user_keyboard()
    )


def main():
    init_db()

    app = Application.builder().token(TOKEN).build()

    register_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Зареєструватися$"), register_start)],
        states={
            REGISTER_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_phone)],
        },
        fallbacks=[CommandHandler("cancel", start)],
    )

    order_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Замовити квиток$"), order_start)],
        states={
            ORDER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_name)],
            ORDER_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_phone)],
            ORDER_SHOW: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_show)],
            ORDER_COUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_count)],
            ORDER_COMMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_comment)],
        },
        fallbacks=[CommandHandler("cancel", start)],
    )

    support_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Написати адміну$"), support_start)],
        states={
            SUPPORT_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, support_message)],
        },
        fallbacks=[CommandHandler("cancel", start)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("shows", shows_command))
    app.add_handler(CommandHandler("users", users_command))
    app.add_handler(CommandHandler("orders", orders_command))
    app.add_handler(CommandHandler("addshow", addshow_command))
    app.add_handler(CommandHandler("confirm_order", confirm_order_command))
    app.add_handler(CommandHandler("cancel_order", cancel_order_command))
    app.add_handler(CommandHandler("reply", reply_command))
    app.add_handler(CommandHandler("broadcast", broadcast_command))

    app.add_handler(register_handler)
    app.add_handler(order_handler)
    app.add_handler(support_handler)

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback_text))

    print("Бот запущено...")
    app.run_polling()


if __name__ == "__main__":
    main()