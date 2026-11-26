import logging
import os

import vk_api
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
from vk_api.utils import get_random_id


def required(name):
    value = os.environ.get(name, "").strip()
    if not value:
        raise SystemExit(f"Укажите {name} в окружении.")
    return value


def main():
    token = required("VK_ACCESS_TOKEN")
    try:
        group_id = int(required("VK_GROUP_ID"))
        peer_id = int(required("VK_CHAT_PEER_ID"))
        if group_id <= 0 or peer_id < 2_000_000_000:
            raise ValueError
    except ValueError:
        raise SystemExit("Укажите положительный VK_GROUP_ID и VK_CHAT_PEER_ID беседы.") from None
    words = {word.strip().casefold() for word in os.getenv("VK_RULE_WORDS", "привет,пока").split(",") if word.strip()}
    try:
        session = vk_api.VkApi(token=token)
        api = session.get_api()
        for event in VkBotLongPoll(session, group_id).listen():
            if event.type != VkBotEventType.MESSAGE_NEW:
                continue
            message = event.object.message
            if message.get("peer_id") != peer_id or message.get("out"):
                continue
            if message.get("text", "").strip().casefold() in words:
                api.messages.send(
                    peer_id=peer_id,
                    message="Напоминание о правилах беседы.",
                    random_id=get_random_id(),
                )
    except (vk_api.VkApiError, OSError):
        logging.error("Подключение к VK прервано. Проверьте настройки сообщества и ключа.")
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
