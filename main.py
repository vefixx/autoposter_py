import os
from colorama import init, Fore
import json
from fake_useragent import UserAgent
import asyncio
import datetime
from data.database import database
import aiohttp
from aiohttp import FormData


init(autoreset=True)


async def addlogs(text: str):
    with open('logs.txt', 'a', encoding='utf-8') as file:
        current_datetime = datetime.datetime.now()
        formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
        file.write(f'[{formatted_datetime}] {text}\n')
        file.close()

async def send_message(channel_id, token, text, image_ids=None):
    """Отправляет запрос на отправку сообщения"""
    ua = UserAgent()
    user_agent = ua.random
    payload = {"content": str(text)}    # Загружаем в dat'у наш текст
    headers = {"authorization": token, 'User-Agent': user_agent}    # хедерс, передаем токен и юзер агент - чтобы не засчитали как спам

    data = FormData()
    data.add_field("payload_json", json.dumps(payload))

    """Проверка добавления картинок"""
    if image_ids is not None and isinstance(image_ids, list):
        for i, image_id in enumerate(image_ids):
            try:
                image_path = f'data/images/{image_id}'
                if os.path.exists(f"{image_path}"):
                    data.add_field(f"file{i + 1}", open(f"{image_path}", "rb"))
            except Exception as e:
                pass

    """Отправка сообщения"""
    async with aiohttp.ClientSession() as session:
        url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
        async with session.post(url, headers=headers, data=data) as response:
            status_code = response.status
            await addlogs(f'Сообщение отправлено с кодом {status_code} / Канал отправки {channel_id} / Файлы {image_ids}')
            return status_code  # Возвращаем наш статус

async def checkout_request(request):
    token = request[0]
    channelid = request[1]
    text = request[2]
    images = request[3]
    cooldown = request[4]
    constCooldown = request[5]
    id = request[6]
    if None in request:
        if images is None: # Проверяем, что пустая строка это не картинки
            ...
        else:
            """Значит что реквест еще не заполнился"""
            """Заканчиваем функцию и возвращаем 0"""
            print(Fore.RED + f'Не законченная строка')
            return 0

    if cooldown != 0:
        """Уменьшаем кд на 1 секунду"""
        new_cooldown = cooldown - 1
        await database.updateTime(id, new_cooldown) # задаем новое время
        return 0  # возвращаем 0, чтобы функция не продолжала сове действие
    if images is not None:
        images = images.split(', ')  # превращаем наши перечисления в массив
        if images == []:
            images = None

    """Если все проверки прошли, то запускаем нашу отправку"""
    await database.updateTime(id, constCooldown)  # Берем constCooldown как изначальное время
    status_code = await send_message(channelid, token, text, images)
    print(Fore.LIGHTCYAN_EX + f'Сообщение №{id} отправлено с кодом {status_code}')

    # Обновляем время до изначального


async def send_messages_and_update():
    """
    Каждую секунду создает новые потоки со всеми реквестами в базе.
    :return:
    """
    while True:
        await asyncio.sleep(1)
        all_requests = await database.getAllRequests()
        if all_requests is not None:  # обработать событие для проверки реквеста
            """Делаем так, чтобы реквесты не мешали друг другу и каждый реквест выполнялся в своем потоке."""
            tasks = [checkout_request(request) for request in all_requests]
            all_tasks = tasks
            asyncio.ensure_future(asyncio.gather(*all_tasks))  # запуск

            print(Fore.LIGHTMAGENTA_EX + f'Круг закончился')
        else:
            print(Fore.RED + f'Нет реквестов в базе!!')



async def main():
    loop = asyncio.get_event_loop()
    tasks = [loop.create_task(send_messages_and_update())]

    # Запуск асинхронных задач
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    print(Fore.LIGHTBLUE_EX + f'Старт скрипта')
    asyncio.run(main())
