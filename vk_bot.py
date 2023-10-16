import sys
import logging
from environs import Env

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

logger = logging.getLogger(__name__)


def vk_keyboard(event, vk):
    keyboard = VkKeyboard()

    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)

    keyboard.add_line()
    keyboard.add_button('Мой счёт', color=VkKeyboardColor.SECONDARY)

    vk.messages.send(
        peer_id=event.user_id,
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard(),
        message=event.text
    )


def main():
    env = Env()
    env.read_env()

    vk_token = env('VK_TOKEN')
    vk_session = vk_api.VkApi(token=vk_token)
    api_vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            vk_keyboard(event, api_vk)


if __name__ == "__main__":
    logging.getLogger(__name__).setLevel(logging.DEBUG)
    try:
        main()
    except KeyboardInterrupt:
        sys.exit()