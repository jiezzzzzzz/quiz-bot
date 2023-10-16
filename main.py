import logging

import telegram
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

custom_keyboard = [['кнопка раз', 'кнопка двас'],
                   ['кнопка трис', 'кнопка четырес']]


def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    update.message.reply_markdown_v2(
        fr'Здравствуйте\!',
        reply_markup=reply_markup,

    )


def echo(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(update.message.text)


def main() -> None:
    updater = Updater("5728727104:AAFPQl8McbB_DVlJqW56dseqS1uoHQFKWHc")

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()

if __name__ == '__main__':
    main()