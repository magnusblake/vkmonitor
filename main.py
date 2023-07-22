# -*- coding: utf-8 -*-
# [Импорт необходимых модулей] #
import aiohttp
import asyncio
import aiosqlite
import json
from aiogram import Bot, Dispatcher
from datetime import datetime
from config import *
from babel.dates import format_date

# [Инициализация объекта бота и диспетчера] #
bot = Bot(token=telegramToken)
botDispatcher = Dispatcher(bot)
 
async def databaseExecute(query, parameters=()):
    async with aiosqlite.connect(databaseName) as database:
        databaseCursor = await database.cursor()
        await databaseCursor.execute(query, parameters)
        await database.commit()

async def databaseFetchone(query, parameters=()):
    async with aiosqlite.connect(databaseName) as database:
        databaseCursor = await database.cursor()
        await databaseCursor.execute(query, parameters)
        databaseRow = await databaseCursor.fetchone()
        return databaseRow

async def databaseCreate():
    await databaseExecute("""
    CREATE TABLE IF NOT EXISTS botState (
        id INTEGER PRIMARY KEY,
        lastReportTime REAL,
        subscribersCount TEXT
    )
    """)

    if not await databaseFetchone("SELECT * FROM botState WHERE id = 1"):
        await databaseExecute("""
        INSERT INTO botState (id, lastReportTime, subscribersCount)
        VALUES (1, ?, ?)
        """, (datetime.now().timestamp(), json.dumps({group_id: 0 for group_id in vkGroupsID})))

async def getLastReportTime():
    row = await databaseFetchone("SELECT lastReportTime FROM botState WHERE id = 1")
    return datetime.fromtimestamp(row[0])

async def setLastReportTime(time):
    await databaseExecute("UPDATE botState SET lastReportTime = ? WHERE id = 1", (time.timestamp(),))

async def getCountSubscribersPrevious():
    row = await databaseFetchone("SELECT subscribersCount FROM botState WHERE id = 1")
    return json.loads(row[0])

async def setCountSubscribersPrevious(count):
    await databaseExecute("UPDATE botState SET subscribersCount = ? WHERE id = 1", (json.dumps(count),))

async def getGroupStats(group_id):
    await asyncio.sleep(1)
    lastReportTime = await getLastReportTime()

    # Получение статистики сообщества
    async with aiohttp.ClientSession() as session:
        # Получаем информацию о сообществе
        getGroupInfo = await session.get(
            vkAPIUrl + 'groups.getById',
            params={
                'access_token': vkToken,
                'v': vkAPIVersion,
                'group_ids': group_id,
                'fields': 'members_count'
            }
        )
        groupInfo = await getGroupInfo.json()
        
        if 'response' in groupInfo:
            groupName = groupInfo['response'][0]['name']
            numberOfSubscribers = groupInfo['response'][0]['members_count']

            # Сохраняем текущее количество подписчиков
            previousSubscribersCount = await getCountSubscribersPrevious()
            currentSubscribersCount = {**previousSubscribersCount, str(group_id): numberOfSubscribers}
            await setCountSubscribersPrevious(currentSubscribersCount)

        # Получаем записи с момента последнего отчета
        now = datetime.now()
        postsResponse = await session.get(
            vkAPIUrl + 'wall.get',
            params={
                'access_token': vkToken,
                'v': vkAPIVersion,
                'owner_id': -group_id,
                'count': 100,
                'filter': 'owner',
                'extended': 1
            }
        )
        posts = await postsResponse.json()

        # Количество рекламных постов и общее число постов
        numberOfADPosts = 0
        numberOfPosts = 0
        totalReach = 0

        if 'response' in posts and 'items' in posts['response']:
            for post in posts['response']['items']:
                postDate = datetime.fromtimestamp(post['date'])
                if postDate > lastReportTime:
                    numberOfPosts += 1
                    if post.get('text', '').startswith(specialChar):
                        numberOfADPosts += 1          
            # Вычисление общего охвата
            totalReach = sum(post['views']['count'] for post in posts['response']['items'] if 'views' in post and datetime.fromtimestamp(post['date']) > lastReportTime)
        else:
            print("Ошибка: в ответе от API отсутствует ключ 'response' или 'items'")

        # Получаем количество новых подписчиков
        previousSubscribers = previousSubscribersCount.get(str(group_id), 0)
        newSubscribers = numberOfSubscribers - previousSubscribers

        # Возвращаем результаты
        return groupName, numberOfPosts, newSubscribers, numberOfADPosts, totalReach

async def sendDailyReport():
    # Отправка отчета по каждому сообществу
    tasks = [getGroupStats(group_id) for group_id in vkGroupsID]
    results = await asyncio.gather(*tasks)

    for group_id, result in zip(vkGroupsID, results):
        groupName, groupNewPosts, groupNewSubscribers, groupNewDirectADs, groupCoverage = result
        now = datetime.now()
        reportDate = format_date(now, format="d MMMM", locale=appLocale)
        report_message = (
            f"🔔 Отчёт по сообществу «<a href='https://vk.com/public{group_id}'>{groupName}</a>» за <b>{reportDate}</b>\n\n"
            f"• <b>Опубликовано:</b> {groupNewPosts} постов\n"
            f"• <b>Продано:</b> {groupNewDirectADs} прямых реклам\n\n"
            f"📈 <b>+{groupNewSubscribers}</b> подписчиков\n"
            f"📊 <b>{groupCoverage}</b> охват подписчиков"
        )
        await bot.send_message(chat_id=telegramChatID, text=report_message, parse_mode='HTML', disable_web_page_preview=not(webPagePreview))
        await setLastReportTime(now)
        await asyncio.sleep(1)

async def scheduleDailyReport(hour, minute):
    while True:
        now = datetime.now()
        if now.hour == hour and now.minute == minute:
            await sendDailyReport()
            await asyncio.sleep(60)  # Спим одну минуту, чтобы избежать повторного отправления отчета в ту же минуту
        else:
            await asyncio.sleep(1)  # Если сейчас не время отправки отчета, спим одну секунду и проверяем снова

async def onStartup():
    with open(imageStart, 'rb') as photo:
        await bot.send_photo(chat_id=telegramChatID, photo=photo, caption=f"<b>{captionImageStart}</b>", parse_mode="HTML")
    for group_id in vkGroupsID:
        _, _, _, _, _ = await getGroupStats(group_id)

async def onShutdown():
    with open(imageStop, 'rb') as photo:
        await bot.send_photo(chat_id=telegramChatID, photo=photo, caption=f"<b>{captionImageStop}</b>", parse_mode="HTML")

async def main():
    await databaseCreate()
    await onStartup()
    asyncio.create_task(scheduleDailyReport(timeHours, timeMinutes))  # Запускаем scheduleDailyReport как задачу

    try:
        while True:
            await asyncio.sleep(1)  # Спим, чтобы предотвратить завершение главной функции
    except KeyboardInterrupt:
        print("Ожидайте, идет процесс остановки...")
    except asyncio.exceptions.CancelledError:
        pass  # Игнорируем исключение CancelledError
    finally:
        await onShutdown()

if __name__ == "__main__":
    asyncio.run(main())