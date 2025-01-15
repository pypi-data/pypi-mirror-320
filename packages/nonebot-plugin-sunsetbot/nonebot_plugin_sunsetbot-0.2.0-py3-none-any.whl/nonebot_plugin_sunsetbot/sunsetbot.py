import asyncio
import random
from datetime import datetime

from pydantic import BaseModel
from aiohttp import ClientSession

from typing import Dict, List, Union


class ForecastResult(BaseModel):
    aod: float
    aod_str: str
    quality: float
    quality_str: str
    event_time: datetime


class SunsetBotError(Exception):
    def __init__(self, msg: str):
        self.msg = msg
    
    def __str__(self):
        return self.msg


class SunsetBot:
    BASE_URL = 'https://sunsetbot.top/'

    def __init__(self, headers: Dict = None):
        self._session = None
        if headers is None:
            self._headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                'host': 'sunsetbot.top'
            }
        else:
            self._headers = headers

    async def get_json(self, url: str, params: Dict):
        if self._session is None:
            self._session = ClientSession(headers=self._headers)
        async with self._session.get(url, params=params) as response:
            return await response.json()

    def query_id(self) -> int:
        return int(random.random()*10000000 + 1)

    async def query_city(self, name: str) -> List[str]:
        url = self.BASE_URL
        result_raw = await self.get_json(url, params={'query_id': self.query_id(), 'intend': 'change_city', 'city_name_incomplete': name})
        return result_raw['city_list']

    async def get_forecast(self, city: str, event: str) -> ForecastResult:
        url = self.BASE_URL
        result_raw = await self.get_json(url, params={
            'query_id': self.query_id(), 'intend': 'select_city', 'query_city': city, 'event': event, 'event_date': 'None', 'times': 'None'})
        if result_raw['status'] == 'ok':
            aod, aod_description = result_raw['tb_aod'].strip().split('<br>')
            quality, quality_description = result_raw['tb_quality'].strip().split('<br>')
            result = ForecastResult(
                aod=float(aod), quality=float(quality),
                aod_str=aod+aod_description, quality_str=quality+quality_description,
                event_time = datetime.strptime(
                    result_raw['tb_event_time'], '%Y-%m-%d<br>%H:%M:%S'))
            return result
        else:
            raise SunsetBotError(result_raw['status'])

    async def get_forecast_1day(self, city: str):
        now = datetime.now()
        if now.hour < 5:
            events = ['rise_1', 'set_1']
        elif now.hour < 17:
            events = ['set_1', 'rise_2']
        else:
            events = ['rise_2', 'set_2']
        return await asyncio.gather(*[self.get_forecast(city, event) for event in events])
