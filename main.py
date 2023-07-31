# -*- coding: utf-8 -*-
# [Импорт необходимых модулей] #
import asyncio
from aiogram import Bot, Dispatcher
from config import telegramToken, timeHours, timeMinutes, typeTrigger
from functions import BotFunctions
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# [Инициализация экземпляра класса BotFunctions] #
BotFunctions = BotFunctions()

# [Инициализация объекта бота и диспетчера] #
bot = Bot(token=telegramToken)
botDispatcher = Dispatcher(bot)

# [Инициализация объекта планировщика задач] #
botScheduler = AsyncIOScheduler()
botScheduler.add_job(BotFunctions.sendReport, typeTrigger, hour=timeHours, minute=timeMinutes, args=[bot])

# [Инициализация событийного цикла для текущего контекста выполнения] #
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# [Запуск планировщика задач] #
botScheduler.start()

# [Запуск бесконечного цикла событий] #
try:
    loop.run_until_complete(BotFunctions.onStartup(bot))
    asyncio.get_event_loop().run_forever()
except KeyboardInterrupt:
    loop.run_until_complete(BotFunctions.onShutdown(bot))
