from nonebot import require

require("nonebot_plugin_apscheduler")
require("nonebot_plugin_localstore")


from nonebot import on_command, get_driver
from nonebot.plugin import PluginMetadata

from .handler import sunset_query_handler, city_query_handler, add_schduler_handler, list_user_schedule, delete_user_schedule,\
      on_startup, on_end

from .config import Config

__plugin_meta__ = PluginMetadata(
    name="nonebot-plugin-sunsetbot",
    description="SunsetBot朝霞晚霞查询",
    usage="特定时间预报：[今天/明天][朝霞/晚霞] [地区名]\n"
          "地名精确到市或区，如：今天朝霞 上海；今天朝霞 上海-徐汇区\n"
          "未来一天预报：火烧云 [地区名]\n"
          "地区名需精确匹配。查询地区名：火烧云地区 [部分地区名]\n"
          "每日定时提醒某地区火烧云状态：火烧云订阅 [地区名]\n"
          "查看订阅列表：火烧云订阅 查看\n"
          "取消订阅：火烧云订阅 [取消/删除] [地区名]\n",
    type="application",
    supported_adapters={"~onebot.v11", "~console"},
    config=Config,
)


events_map = {'今天朝霞': 'rise_1', '今天晚霞': 'set_1', '明天朝霞': 'rise_2', '明天晚霞': 'set_2'}
for cmd, event in events_map.items():
    matcher = on_command(cmd, block=True)
    matcher.handle()(sunset_query_handler(event))
on_command("火烧云", block=True).handle()(sunset_query_handler('1day'))

on_command("火烧云地区", block=True).handle()(city_query_handler)

on_command("火烧云订阅", block=True).handle()(add_schduler_handler)

on_command(("火烧云订阅", "查看"), block=True).handle()(list_user_schedule)
on_command(("火烧云订阅", "删除"), aliases={("火烧云订阅", "取消")}, block=True).handle()(delete_user_schedule)


driver = get_driver()
driver.on_bot_connect(on_startup)
driver.on_bot_disconnect(on_end)
