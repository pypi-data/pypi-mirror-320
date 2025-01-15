import aiosqlite
from pydantic import BaseModel

from typing import List, Optional


class ScheduleData(BaseModel):
    id: int
    city: str
    user_id: str
    group_id: Optional[str]
    threshold: float


class ScheduleDb:
    def __init__(self, path):
        self.db = aiosqlite.connect(path)

    async def fetch(self, sql: str, args = None):
        async with self.db.cursor() as cursor:
            if args is None:
                result = await cursor.execute(sql)
            else:
                result = await cursor.execute(sql, args)
            return await result.fetchall()

    async def async_init(self):
        await self.db
        async with self.db.cursor() as cursor:
            await cursor.execute("CREATE TABLE IF NOT EXISTS schedule (id INTEGER PRIMARY KEY autoincrement, city TEXT, user_id TEXT, group_id TEXT, threshold REAL)")
            await cursor.execute("PRAGMA table_info(schedule);")
            columns = await cursor.fetchall()
            if not any(column[1] == 'threshold' for column in columns):
                await cursor.execute("ALTER TABLE schedule ADD COLUMN threshold REAL")  # 添加新列
            await self.db.commit()

    async def insert_schedule(self, city: str, user_id: str, group_id: str = None, threshold: float = 0) -> int:
        async with self.db.cursor() as cursor:
            await cursor.execute("INSERT INTO schedule(city,user_id,group_id,threshold) VALUES (?,?,?,?)", (city,user_id,group_id,threshold))
            result = await cursor.execute('select last_insert_rowid() from schedule LIMIT 1;')
            last_id = (await result.fetchone())[0]
            await self.db.commit()
        return last_id
    
    async def delete_schedule(self, id: int):
        async with self.db.cursor() as cursor:
            await cursor.execute("DELETE FROM schedule WHERE id=(?)", (id,))
            await self.db.commit()

    async def get_all_schedule(self) -> List[ScheduleData]:
        schedules = await self.fetch("SELECT id,city,user_id,group_id,threshold FROM schedule")
        return [ScheduleData(id=line[0], city=line[1], user_id=line[2], group_id=line[3], threshold=line[4])
                for line in schedules]

    async def close(self):
        await self.db.close()
