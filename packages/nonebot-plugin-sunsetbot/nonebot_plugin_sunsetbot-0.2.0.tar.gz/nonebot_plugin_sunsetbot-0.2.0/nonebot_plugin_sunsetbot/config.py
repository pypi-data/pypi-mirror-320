from pydantic import BaseModel
from typing import Dict


class ScopedConfig(BaseModel):
    db_path: str = "sunsetbot.db"

    schedule_trigger: str = "cron"
    schedule_timezone: str = "Asia/Shanghai"
    schedule_gracetime: float = 300
    schedule_sleep_range: float = 10
    schedule_kwargs: Dict = {"hour": "14,21"}
    schedule_message: str = "每日14:00和21:00"

    schedule_quality_threshold: float = 0.1
    schedule_badforcast_msg: str = "{city}未来一天内没有超过阈值的火烧云"


class Config(BaseModel):
    sunsetbot: ScopedConfig = ScopedConfig()