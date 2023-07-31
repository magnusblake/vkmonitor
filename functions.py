# -*- coding: utf-8 -*-
# [Импорт необходимых модулей] #
import aiovk
import datetime
import asyncio
from config import telegramChatID, vkToken, groupIDs, specialChar, imagesGroup, appLocale, captionImageStart, captionImageStop, imageStart, imageStop
from babel.dates import format_date
import time
import pymorphy3

# [Инициализация класса для работы со всеми функциями бота] #
class BotFunctions:
    async def getGroupName(self, vkToken, groupID):
        """
        Получение названия группы по её ID
        """
        session = aiovk.TokenSession(access_token=vkToken)
        api = aiovk.API(session=session)
        response = await api.groups.getById(group_ids=str(groupID))
        groupName = response[0]['name']
        await session.close()
        return groupName

    async def getGroupStats(self, vkToken, groupID):
        """
        Получение статистики группы по её ID
        """
        session = aiovk.TokenSession(access_token=vkToken)
        api = aiovk.API(session=session)
        stats = await api.stats.get(group_id=groupID, interval='day', intervals_count=1)
        reachTotal = stats[0]['reach']['reach']
        reachSubscribers = stats[0]['reach']['reach_subscribers']
        totalReposts = stats[0].get('activity', {}).get('copies', 0)
        totalSubscribed = stats[0].get('activity', {}).get('subscribed', 0)
        totalUnsubscribed = stats[0].get('activity', {}).get('unsubscribed', 0)
        await session.close()
        return reachSubscribers, reachTotal, totalReposts, totalSubscribed, totalUnsubscribed

    async def getGroupPosts(self, vkToken, groupID):
        """
        Получение количества постов группы за последние сутки по её ID
        """
        session = aiovk.TokenSession(access_token=vkToken)
        api = aiovk.API(session=session)
        timeNow = int(time.time())
        timeDayAgo = timeNow - (24 * 60 * 60)
        postsResponse = await api.wall.get(owner_id=f"-{groupID}")
        await session.close()
        totalPosts = 0
        totalAdPosts = 0
        totalMarketPosts = 0
        for post in postsResponse['items']:
            if 'date' in post and post['date'] > timeDayAgo:
                totalPosts += 1
                if 'marked_as_ads' in post and post['marked_as_ads'] == 1:
                    totalMarketPosts += 1
                if specialChar in post.get('text', ''):
                    totalAdPosts += 1
        return totalPosts, totalAdPosts, totalMarketPosts

    async def sendReport(self, bot):
        """
        Отправка отчётов о группах в чат Telegram
        """
        morph = pymorphy3.MorphAnalyzer()
        for groupID in groupIDs:
            stats = await self.getGroupStats(vkToken, groupID)
            totalPosts, totalAdPosts, totalMarketPosts = await self.getGroupPosts(vkToken, groupID)
            groupName = await self.getGroupName(vkToken, groupID)
            timeNow = datetime.datetime.now()
            timeDayAgo = timeNow - datetime.timedelta(days=1)
            reportDate = format_date(timeDayAgo, format="d MMMM", locale=appLocale)
            subscribersDifference = stats[3] - stats[4]
            pSubscribers = morph.parse('подписчик')[0]
            if subscribersDifference > 0:
                subscribersDifferenceStr = f"+<b>{subscribersDifference}</b> {pSubscribers.inflect({'nomn', 'sing'}).word}"
            elif subscribersDifference < 0:
                subscribersDifferenceStr = f"<b>{subscribersDifference}</b> {pSubscribers.inflect({'gent', 'sing'}).word}"
            else:
                subscribersDifferenceStr = "<b>+0</b> подписчиков"
            pPosts = morph.parse('пост')[0]
            pReposts = morph.parse('репост')[0]
            pMarket = morph.parse('биржа')[0]
            pDirect = morph.parse('прямая')[0]
            pAd = morph.parse('реклама')[0]
            messageCaption = (
                f"🔔 Отчёт по сообществу «<a href='https://vk.com/public{groupID}'>{groupName}</a>» за <b>{reportDate}</b>\n\n"
                f"• <b>Опубликовано:</b> {totalPosts} {pPosts.make_agree_with_number(totalPosts).word}\n"
                f"• <b>Продано:</b> {totalAdPosts} {pDirect.make_agree_with_number(totalAdPosts).word} {pAd.make_agree_with_number(totalAdPosts).word}, {totalMarketPosts} {pMarket.make_agree_with_number(totalMarketPosts).word}\n\n"
                f"👤 {subscribersDifferenceStr}\n"
                f"📢 <b>{stats[2]}</b> {pReposts.make_agree_with_number(stats[2]).word}\n"
                f"🔍 <b>{stats[1]}</b> общий охват\n"
                f"📊 <b>{stats[0]}</b> охват подписчиков"
            )
            with open(imagesGroup[groupID], 'rb') as photo:
                await bot.send_photo(chat_id=telegramChatID, photo=photo, caption=messageCaption, parse_mode='HTML')
            await asyncio.sleep(1)

    async def onStartup(self, bot):
        """
        Отправка сообщения о запуске бота в чат Telegram
        """
        with open(imageStart, 'rb') as photo:
            await bot.send_photo(chat_id=telegramChatID, photo=photo, caption=f"<b>{captionImageStart}</b>", parse_mode='HTML')

    async def onShutdown(self, bot):
        """
        Отправка сообщения об остановке бота в чат Telegram
        """
        with open(imageStop, 'rb') as photo:
            await bot.send_photo(chat_id=telegramChatID, photo=photo, caption=f"<b>{captionImageStop}</b>", parse_mode='HTML')
