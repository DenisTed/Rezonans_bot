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
    add_show,
    get_active_shows,
    add_ticket_order,
    get_last_orders,
    get_user_orders,
    update_order_status,
    get_order_by_id
)

support_mode_users = set()


def is_admin(user_id: int) -> bool:
    return user_id in ADMINS


def get_user_keyboard():
    keyboard = [
        ["Відкрити театр", "Мої квитки"],
        ["Написати адміну", "Контакти"],
        ["Допомога"]
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
        f"Ви зареєстровані в боті театру “Резонанс”.\n"
        f"Оберіть дію кнопками нижче.",
        reply_markup=get_user_keyboard()
    )


async def open_theatre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Відкрити інтерфейс театру", web_app=WebAppInfo(url=WEB_APP_URL))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Натисніть кнопку нижче, щоб відкрити інтерфейс театру:",
        reply_markup=reply_markup
    )


async def my_tickets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    orders = get_user_orders(user_id)

    if not orders:
        await update.message.reply_text("У вас поки немає замовлень квитків.")
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


async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    support_mode_users.add(user_id)

    await update.message.reply_text(
        "Напишіть повідомлення адміністратору.\n"
        "Для виходу з режиму використайте /cancel"
    )


async def contacts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Контакти театру “Резонанс”:\n\n"
        "Адреса: м. Кропивницький, вул. Театральна, 12\n"
        "Телефон: +38 (050) 123-45-67\n"
        "Email: rezonans.theatre@gmail.com"
    )


async def help_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Що можна зробити:\n\n"
        "Відкрити театр — переглянути афішу та квитки\n"
        "Мої квитки — переглянути свої заявки\n"
        "Написати адміну — поставити питання\n"
        "Контакти — переглянути контакти театру"
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

    text = "Список користувачів:\n\n"
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

    if len(context.args) < 3:
        await update.message.reply_text(
            "Формат: /addshow Назва | Дата | Час | Опис\n"
            "Приклад:\n"
            "/addshow Випадок у психолога | 2026-05-20 | 18:00 | Прем'єра сезону"
        )
        return

    raw = " ".join(context.args)
    parts = [p.strip() for p in raw.split("|")]

    if len(parts) < 3:
        await update.message.reply_text("Мало даних. Потрібно: Назва | Дата | Час | Опис")
        return

    title = parts[0]
    show_date = parts[1]
    show_time = parts[2]
    description = parts[3] if len(parts) > 3 else ""

    add_show(title, show_date, show_time, description)
    await update.message.reply_text(f"Виставу '{title}' додано.")


async def shows_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    shows = get_active_shows()

    if not shows:
        await update.message.reply_text("Активних вистав поки немає.")
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


async def confirm_order_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    if len(context.args) != 1:
        await update.message.reply_text("Формат: /confirm_order order_id")
        return

    try:
        order_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("order_id має бути числом.")
        return

    order = get_order_by_id(order_id)
    if not order:
        await update.message.reply_text("Заявку не знайдено.")
        return

    updated = update_order_status(order_id, "confirmed")
    if not updated:
        await update.message.reply_text("Не вдалося оновити статус.")
        return

    _, user_id, customer_name, _, show_name, ticket_count, _, _, _ = order

    await update.message.reply_text(f"Заявка №{order_id} підтверджена.")

    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                f"Вашу заявку №{order_id} підтверджено.\n\n"
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

    try:
        order_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("order_id має бути числом.")
        return

    order = get_order_by_id(order_id)
    if not order:
        await update.message.reply_text("Заявку не знайдено.")
        return

    updated = update_order_status(order_id, "canceled")
    if not updated:
        await update.message.reply_text("Не вдалося оновити статус.")
        return

    _, user_id, customer_name, _, show_name, ticket_count, _, _, _ = order

    await update.message.reply_text(f"Заявка №{order_id} скасована.")

    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                f"Вашу заявку №{order_id} скасовано.\n\n"
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

    try:
        user_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("user_id має бути числом.")
        return

    text = " ".join(context.args[1:])

    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"Повідомлення від адміністратора:\n\n{text}"
        )
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
                text=f"Новина від театру “Резонанс”:\n\n{text}"
            )
            sent += 1
        except Exception:
            failed += 1

    await update.message.reply_text(
        f"Розсилку завершено.\n"
        f"Успішно: {sent}\n"
        f"Не вдалося: {failed}"
    )


async def handle_webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw_data = update.message.web_app_data.data
    user = update.effective_user

    try:
        data = json.loads(raw_data)
        action = data.get("action")

        if action == "ticket_request":
            customer_name = data.get("name", "")
            phone = data.get("phone", "")
            show = data.get("show", "")
            count = data.get("count", "")
            comment = data.get("comment", "")

            order_id = add_ticket_order(user.id, customer_name, phone, show, count, comment)

            await update.message.reply_text(
                f"Вашу заявку №{order_id} прийнято.\n"
                f"Статус: new\n"
                f"Адміністратор зв’яжеться з вами тут у боті."
            )

            admin_text = (
                f"Нова заявка на квитки\n\n"
                f"Заявка №{order_id}\n"
                f"User ID: {user.id}\n"
                f"Ім’я: {customer_name}\n"
                f"Телефон: {phone}\n"
                f"Вистава: {show}\n"
                f"Кількість: {count}\n"
                f"Коментар: {comment if comment else 'немає'}\n"
                f"Статус: new"
            )

            for admin_id in ADMINS:
                await context.bot.send_message(chat_id=admin_id, text=admin_text)

    except Exception as e:
        await update.message.reply_text(f"Помилка обробки даних: {e}")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = (update.message.text or "").strip()

    print(f"Натиснуто текст: {text}")

    if text == "Відкрити театр":
        await open_theatre(update, context)
        return

    if text == "Мої квитки":
        await my_tickets(update, context)
        return

    if text == "Написати адміну":
        await support(update, context)
        return

    if text == "Контакти":
        await contacts(update, context)
        return

    if text == "Допомога":
        await help_text(update, context)
        return

    if user.id in support_mode_users:
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

    # команди адміна
    app.add_handler(CommandHandler("users", users_command))
    app.add_handler(CommandHandler("orders", orders_command))
    app.add_handler(CommandHandler("addshow", addshow_command))
    app.add_handler(CommandHandler("shows", shows_command))
    app.add_handler(CommandHandler("confirm_order", confirm_order_command))
    app.add_handler(CommandHandler("cancel_order", cancel_order_command))
    app.add_handler(CommandHandler("reply", reply_command))
    app.add_handler(CommandHandler("broadcast", broadcast_command))

    # web app
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_webapp_data))

    # текстові кнопки
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("Бот запущено...")
    app.run_polling()


if __name__ == "__main__":
    main()