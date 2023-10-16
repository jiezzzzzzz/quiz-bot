import logging
import redis
import random
import telegram
import os
from environs import Env
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def start(bot, update: Update) -> None:
    keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счёт']]
    reply_markup = telegram.ReplyKeyboardMarkup(keyboard, resize_keyboard=True
                                                )
    bot.message.reply_text(
        chat_id=update.message.chat_id,
        text='Привет! Повикторинимся? :)',
        reply_markup=reply_markup
    )


def ask(bot, update, questions, redis_conn):
    if update.message.text == 'Новый вопрос':
        question, answer = random.choice(list(questions.items()))
        update.message.reply_text(question)
        redis_conn.set(
            update.message.from_user.id,
            question
        )
        r = redis_conn.get(update.message.from_user.id)
        update.message.reply_text(questions.get(r.decode("utf-8")))

        logger.debug(f'{update.message.from_user.id} {question} {answer}')


def main() -> None:
    env = Env()
    env.read_env()
    tg_token = env('TELEGRAM_TOKEN')
    redis_host = env('REDIS_HOST')
    redis_port = env('REDIS_PORT')
    redis_password = env('REDIS_PASSWORD')

    redis_connection = redis.Redis(
        host=redis_host,
        port=redis_port,
        password=redis_password,
        db=0
    )

    updater = Updater(tg_token)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))

    #dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()