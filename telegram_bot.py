import functools
import logging
import random
import re
from environs import Env

import redis
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    RegexHandler,
    Filters,
    ConversationHandler
)

from load_questions import load_questions


logger = logging.getLogger(__name__)

CHOOSING, ATTEMPT = range(2)


def remove_comments(answer):
    return re.sub("[\(\[].*?[\)\]]", "", answer).strip()


def start(bot, update):
    keyboard = [['Новый вопрос', 'Сдаться'], ['Cчёт']]
    kb_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    start_message = (
        'Даров! Жми "новый вопрос", чтобы начать викторину,.\n'
        '/cancel - для отмены.'
    )
    update.message.reply_text(start_message, reply_markup=kb_markup)

    return CHOOSING


def handle_solution_request(bot, update, questions, redis_conn):
    question = random.choice(list(questions.keys()))

    logger.debug(
        f'user_id: {update.message.from_user.id}. '
        f'Question: {question} '
        f'Answer: {questions.get(question)}'
    )

    redis_conn.set(update.message.from_user.id, question)
    update.message.reply_text(question)

    return ATTEMPT


def handle_solution_attempt(bot, update, questions, redis_conn):
    current_question = redis_conn.get(update.message.from_user.id)
    answer = questions.get(current_question)
    user_response = update.message.text
    correct_answer = remove_comments(answer).lower().strip('.')

    logger.debug(
        f'User response: {user_response} '
        f'Correct answer: {correct_answer}'
    )

    if user_response.lower() == correct_answer:
        update.message.reply_text(
            'Ура все верно '
            'Тыкай в "новый вопрос", чтобы продолжить'
        )
        return CHOOSING
    else:
        update.message.reply_text('Неправильно. Пробовать еще раз не советую, но ты можешь')

        return ATTEMPT


def handle_give_up(bot, update, questions, redis_conn):
    current_question = redis_conn.get(update.message.from_user.id)
    answer = questions.get(current_question)
    update.message.reply_text(
        f'Вот тебе правильный ответ: {answer} '
        'Чтобы продолжить нажми "Новый вопрос"'
        'или иди поплачь'
    )

    return CHOOSING


def cancel(bot, update):
    update.message.reply_text(
        f'Покедова, {update.message.from_user.first_name}!',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    env = Env()
    env.read_env()
    questions = load_questions()

    tg_token = env('TELEGRAM_TOKEN')
    redis_host = env('REDIS_HOST')
    redis_port = env('REDIS_PORT')
    redis_password = env('REDIS_PASSWORD')

    redis_conn = redis.Redis(
        host=redis_host,
        port=redis_port,
        password=redis_password,
        charset='utf-8',
        decode_responses=True
    )

    updater = Updater(tg_token)

    dp = updater.dispatcher

    handle_new_question = functools.partial(
        handle_solution_request,
        questions=questions,
        redis_conn=redis_conn
    )

    handle_solution = functools.partial(
        handle_solution_attempt,
        questions=questions,
        redis_conn=redis_conn
    )

    give_up_handle = functools.partial(
        handle_give_up,
        questions=questions,
        redis_conn=redis_conn
    )

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            CHOOSING: [RegexHandler('^Новый вопрос$', handle_new_question)],

            ATTEMPT: [
                RegexHandler('^Сдаться$', give_up_handle),
                MessageHandler(Filters.text, handle_solution)
            ]
        },

        fallbacks=[CommandHandler('cancel', cancel)]

    )

    dp.add_handler(conv_handler)

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    logging.getLogger(__name__).setLevel(logging.DEBUG)
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    main()