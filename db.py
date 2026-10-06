import asyncio
import os

import aiosqlite

# Chỉ cho phép các cột này làm cooldown (tránh SQL injection qua tên cột)
COOLDOWN_COLUMNS = {"last_daily", "last_work"}


class Database:
    def __init__(self, path: str = "data/bot.db"):
        self.path = path
        self.conn: aiosqlite.Connection | None = None
        self.lock = asyncio.Lock()

    async def connect(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self.conn = await aiosqlite.connect(self.path)
        await self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id    INTEGER PRIMARY KEY,
                balance    INTEGER NOT NULL DEFAULT 0,
                last_daily REAL    NOT NULL DEFAULT 0,
                last_work  REAL    NOT NULL DEFAULT 0
            )
            """
        )
        await self.conn.commit()

    async def close(self):
        if self.conn:
            await self.conn.close()

    async def _ensure_user(self, user_id: int):
        await self.conn.execute(
            "INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,)
        )

    async def get_balance(self, user_id: int) -> int:
        async with self.lock:
            await self._ensure_user(user_id)
            cur = await self.conn.execute(
                "SELECT balance FROM users WHERE user_id = ?", (user_id,)
            )
            row = await cur.fetchone()
            await self.conn.commit()
            return row[0]

    async def add_balance(self, user_id: int, amount: int) -> int:
        async with self.lock:
            await self._ensure_user(user_id)
            await self.conn.execute(
                "UPDATE users SET balance = balance + ? WHERE user_id = ?",
                (amount, user_id),
            )
            cur = await self.conn.execute(
                "SELECT balance FROM users WHERE user_id = ?", (user_id,)
            )
            row = await cur.fetchone()
            await self.conn.commit()
            return row[0]

    async def get_cooldown(self, user_id: int, column: str) -> float:
        if column not in COOLDOWN_COLUMNS:
            raise ValueError("Cột cooldown không hợp lệ")
        async with self.lock:
            await self._ensure_user(user_id)
            cur = await self.conn.execute(
                f"SELECT {column} FROM users WHERE user_id = ?", (user_id,)
            )
            row = await cur.fetchone()
            await self.conn.commit()
            return row[0]

    async def set_cooldown(self, user_id: int, column: str, timestamp: float):
        if column not in COOLDOWN_COLUMNS:
            raise ValueError("Cột cooldown không hợp lệ")
        async with self.lock:
            await self._ensure_user(user_id)
            await self.conn.execute(
                f"UPDATE users SET {column} = ? WHERE user_id = ?",
                (timestamp, user_id),
            )
            await self.conn.commit()

    async def transfer(self, from_id: int, to_id: int, amount: int) -> bool:
        """Chuyển tiền an toàn. Trả về False nếu không đủ số dư."""
        async with self.lock:
            await self._ensure_user(from_id)
            await self._ensure_user(to_id)
            cur = await self.conn.execute(
                "SELECT balance FROM users WHERE user_id = ?", (from_id,)
            )
            (balance,) = await cur.fetchone()
            if balance < amount:
                await self.conn.commit()
                return False
            await self.conn.execute(
                "UPDATE users SET balance = balance - ? WHERE user_id = ?",
                (amount, from_id),
            )
            await self.conn.execute(
                "UPDATE users SET balance = balance + ? WHERE user_id = ?",
                (amount, to_id),
            )
            await self.conn.commit()
            return True

    async def leaderboard(self, limit: int = 10):
        async with self.lock:
            cur = await self.conn.execute(
                "SELECT user_id, balance FROM users ORDER BY balance DESC LIMIT ?",
                (limit,),
            )
            return await cur.fetchall()
