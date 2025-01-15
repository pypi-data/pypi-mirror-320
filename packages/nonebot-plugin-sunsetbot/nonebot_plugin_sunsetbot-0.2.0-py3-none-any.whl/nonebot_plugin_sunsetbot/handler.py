import asyncio
import random

from nonebot import get_bot, get_plugin_config, logger
from nonebot.matcher import Matcher
from nonebot.adapters import Message
from nonebot.adapters.console import MessageEvent as MessageEventConsole, Bot as ConsoleBot
from nonebot.adapters.onebot.v11 import MessageEvent as MessageEventOnebotv11, GroupMessageEvent as GroupMessageEventOnebotv11, Bot as Onebotv11
from nonebot.params import CommandArg

from nonebot_plugin_apscheduler import scheduler
import nonebot_plugin_localstore as store

from .sunsetbot import SunsetBot, ForecastResult
from .db import ScheduleDb
from .config import Config

from typing import List, Union

MessageEvent = Union[MessageEventConsole, MessageEventOnebotv11]


sunset_api = SunsetBot()
config = get_plugin_config(Config).sunsetbot

db_path = store.get_plugin_data_file(config.db_path)
db = ScheduleDb(db_path)


def forecast_result_output(city: str, result: Union[ForecastResult, List[ForecastResult]], time_format: str = '%Y-%m-%d %H:%M:%S') -> str:
    if isinstance(result, list):
        return f"{city}的火烧云预报：\n" + "\n\n".join(
            f"{r.event_time.strftime(time_format)}\n鲜艳度：{r.quality_str}\n气溶胶：{r.aod_str}" for r in result)
    else:
        return f"{city}在{result.event_time.strftime(time_format)}的火烧云预报：\n" \
            f"鲜艳度：{result.quality_str}\n气溶胶：{result.aod_str}"


def sunset_query_handler(event_type: str):
    async def handler(matcher: Matcher, args: Message = CommandArg()):
        city = args.extract_plain_text()

        try:
            if event_type == '1day':
                result = await sunset_api.get_forecast_1day(city)
            else:
                result = await sunset_api.get_forecast(city, event_type)
        except Exception as e:
            await matcher.finish(f"查询失败: {e}")
        else:
            await matcher.finish(forecast_result_output(city, result))
    return handler


async def city_query_handler(matcher: Matcher, args: Message = CommandArg()):
    city = args.extract_plain_text()
    try:
        city_list = await sunset_api.query_city(city)
    except Exception as e:
        await matcher.finish(f"查询失败: {e}")
    else:
        if not city_list:
            await matcher.finish("未找到相关城市")
        else:
            await matcher.finish("查询结果：\n"+"\n".join(city_list))


class Context:
    def __init__(self, user_id: str, group_id: str = "-1"):
        self.user_id = user_id
        self.group_id = group_id

    @classmethod
    def from_event(cls, event: MessageEvent):
        if isinstance(event, MessageEventConsole):
            return cls("USER_CONSOLE", "GROUP_CONSOLE")
        elif isinstance(event, GroupMessageEventOnebotv11):
            return cls(event.user_id, event.group_id)
        else:
            return cls(event.user_id)


async def add_schduler_handler(matcher: Matcher, event: MessageEvent, args: Message = CommandArg()):
    context = Context.from_event(event)
    city = args.extract_plain_text().strip()
    schedule_exist = await db.fetch("SELECT id FROM schedule WHERE city=(?) AND user_id=(?) AND group_id=(?)",
                                    (city, context.user_id, context.group_id))
    if schedule_exist:
        await matcher.finish("已订阅过")

    job_id = await db.insert_schedule(city, context.user_id, context.group_id)
    scheduler.add_job(sunset_query_schedule_job, timezone=config.schedule_timezone, misfire_grace_time=config.schedule_gracetime,
                      id=str(job_id), args=(city, context.user_id, context.group_id),
                      trigger=config.schedule_trigger, **config.schedule_kwargs)
    logger.info(f"add job ID {job_id}: user_id={context.user_id}, group_id={context.group_id}, city={city}")
    await matcher.finish(f"已订阅{city}的火烧云预报，{config.schedule_message}更新")


async def list_user_schedule(matcher: Matcher, event: MessageEvent):
    context = Context.from_event(event)
    schedules = await db.fetch("SELECT city FROM schedule WHERE user_id=(?) AND group_id=(?)", (context.user_id, context.group_id))

    if not schedules:
        await matcher.finish(f"无订阅", at_sender=True)

    user = "你" if context.group_id == "-1" else ""
    await matcher.finish(f"{user}的订阅：\n"+"\n".join(f"{s[0]}" for s in schedules), at_sender=True)


async def delete_user_schedule(matcher: Matcher, event: MessageEvent, args: Message = CommandArg()):
    context = Context.from_event(event)
    delete_city = args.extract_plain_text().strip()
    delete_id = await db.fetch("SELECT id FROM schedule WHERE user_id=(?) AND group_id=(?) AND city=(?)",
                               (context.user_id, context.group_id, delete_city))
    if not delete_id:
        await matcher.finish(f"你的订阅中没有：{delete_city}")

    delete_id = delete_id[0][0]
    await db.delete_schedule(delete_id)
    scheduler.remove_job(str(delete_id))
    logger.info(f"delete job ID {delete_id}: user_id={context.user_id}, group_id={context.group_id}, city={delete_city}")
    await matcher.finish(f"已取消{delete_city}的订阅")


async def sunset_query_schedule_job(city: str, user_id: str, group_id: str = "-1"):
    await asyncio.sleep(random.random()*config.schedule_sleep_range)

    bot: Union[ConsoleBot, Onebotv11] = get_bot()
    if isinstance(bot, ConsoleBot):
        # 测试用
        from datetime import datetime
        results = []
        for _ in range(2):
            mock_aod = random.random()
            mock_quality = random.random()*0.5
            results.append(ForecastResult(
                aod=mock_aod, aod_str=f"mock aod {mock_aod:.2f}", quality=mock_quality, quality_str=f"mock quality {mock_quality:.2f}",
                event_time=datetime.now()))
    else:
        results = await sunset_api.get_forecast_1day(city)
    results_valid = [r for r in results if r.quality >= config.schedule_quality_threshold]
    if results_valid or config.schedule_badforcast_msg:
        msg = forecast_result_output(city, results_valid) if results_valid else config.schedule_badforcast_msg.format(city=city)
        if isinstance(bot, ConsoleBot):
            from nonebot.adapters.console import Message as MessageConsoleAdapter
            await bot.send_msg(user_id=user_id, message=MessageConsoleAdapter(msg))
        else:
            if group_id != "-1":
                msg = f"[CQ:at,qq={user_id}]的订阅：\n{msg}"
                logger.debug(f"schedule job: send group message to user {user_id} in group {group_id}")
                await bot.send_group_msg(group_id=group_id, message=msg)
            else:
                logger.debug(f"schedule job: send private message to user {user_id}")
                await bot.send_private_msg(user_id=user_id, message=msg)
    else:
        logger.debug(f"schedule job: no valid forecast for {city}")


async def on_startup():
    await db.async_init()

    all_schedule = await db.get_all_schedule()
    for schedule in all_schedule:
        logger.info(f"load job ID {schedule.id} from disk: user_id={schedule.user_id}, group_id={schedule.group_id}, city={schedule.city}")
        scheduler.add_job(sunset_query_schedule_job, timezone=config.schedule_timezone, misfire_grace_time=config.schedule_gracetime,
                          id=str(schedule.id), args=(schedule.city, schedule.user_id, schedule.group_id),
                          trigger=config.schedule_trigger, **config.schedule_kwargs) 
    
    scheduler.get_jobs()


async def on_end():
    await db.close()
