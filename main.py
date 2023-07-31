# -*- coding: utf-8 -*-
# [Импорт необходимых модулей] #
import asyncio
from aiogram import Bot, Dispatcher
from config import telegramToken, timeHours, timeMinutes, typeTrigger, timeZone
from functions import BotFunctions
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
import pytz
from datetime import time, datetime

# [Инициализация экземпляра класса BotFunctions] #
BotFunctions = BotFunctions()

# [Инициализация объекта бота и диспетчера] #
bot = Bot(token=telegramToken)
botDispatcher = Dispatcher(bot)

# [Инициализация объекта временной зоны] #
timeZoneObj = pytz.timezone(timeZone)
currentTime = time(hour=timeHours, minute=timeMinutes, tzinfo=timeZoneObj)

# [Инициализация объекта планировщика задач] #
botScheduler = AsyncIOScheduler()
runTime = datetime.now(timeZoneObj).replace(hour=currentTime.hour, minute=currentTime.minute)
botScheduler.add_job(BotFunctions.sendReport, DateTrigger(run_date=runTime), args=[bot])

# [Инициализация событийного цикла для текущего контекста выполнения] #
botLoop = asyncio.new_event_loop()
asyncio.set_event_loop(botLoop)

# [Запуск планировщика задач] #
botScheduler.start()

# [Запуск бесконечного цикла событий] #
try:
    botLoop.run_until_complete(BotFunctions.onStartup(bot))
    asyncio.get_event_loop().run_forever()
except KeyboardInterrupt:
    botLoop.run_until_complete(BotFunctions.onShutdown(bot))
