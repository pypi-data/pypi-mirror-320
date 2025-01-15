# nonebot-plugin-sunsetbot

## 功能

查询[Sunsetbot网站](https://sunsetbot.top/)并订阅特定地区通知。

命令：
- 特定时间预报：[今天/明天][朝霞/晚霞] [地区名]
  - 地名精确到市或区，需精确匹配。如：今天朝霞 上海；今天朝霞 上海-徐汇区
- 未来一天预报：火烧云 [地区名]
- 查询地区名：火烧云地区 [部分地区名]
- 每日定时提醒某地区火烧云状态：火烧云订阅 [地区名]
  - 查看订阅列表：火烧云订阅 查看
  - 取消订阅：火烧云订阅 [取消/删除] [地区名]

## 安装

```
pip install nonebot-plugin-sunsetbot
```

## 配置

数据库配置：
- `SUNSETBOT__DB_PATH`: `SQLite`数据库的文件名。默认为`sunsetbot.db`。本项目使用了[nonebot-plugin-localstore](https://github.com/nonebot/plugin-localstore)，数据库文件存储在其定义的`plugin_data_dir`下。

定时提醒配置：
- `SUNSETBOT__SCHEDULE_TRIGGER`：`APScheduler`的`trigger`，默认为`"cron"`
- `SUNSETBOT__SCHEDULE_KWARGS`：设置具体的提醒方式。默认为`{"hour":"14,21"}`，即在每天的14:00、21:00提醒（参考sunsetbot网站的数据更新说明）
- `SUNSETBOT__SCHEDULE_TIMEZONE`: `APScheduler`的时区，默认为东八区（即`Asia/Shanghai`）
- `SUNSETBOT__SCHEDULE_GRACETIME`: `APScheduler`的`misfire_grace_time`参数，默认为`300`
- `SUNSETBOT__SCHEDULE_SLEEP_RANGE`: 为了减轻并发负担，在定时任务唤起时随机sleep一段时间，这一项配置sleep时间的范围，单位为秒。默认为`10`
- `SUNSETBOT__SCHEDULE_MESSAGE`：订阅提醒时向用户发送的信息，与上一项配置对应。默认为`"每日14:00和21:00"`
- `SUNSETBOT__SCHEDULE_QUALITY_THRESHOLD`: 只在火烧云质量大于该值时发送提醒。默认为`0.1`。
- `SUNSETBOT__SCHEDULE_BADFORCAST_MSG`: 在未来一天内没有超过阈值的火烧云时发送的提醒内容。若为空则不发送消息。支持Python的格式化字符串语法，支持的变量为包括：
  - `city`: 订阅的地区名