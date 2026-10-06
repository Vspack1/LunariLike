import asyncio
import logging
import os

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from db import Database

load_dotenv()
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("bot")


class LunariLike(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned,  # chủ yếu dùng slash command
            intents=discord.Intents.default(),
        )
        self.db = Database()

    async def setup_hook(self):
        await self.db.connect()

        # Tự load mọi file trong cogs/
        for filename in sorted(os.listdir("cogs")):
            if filename.endswith(".py") and not filename.startswith("_"):
                await self.load_extension(f"cogs.{filename[:-3]}")
                log.info("Đã load cog: %s", filename)

        self.tree.on_error = self.on_app_command_error

        dev_guild = os.getenv("DEV_GUILD_ID")
        if dev_guild:
            guild = discord.Object(int(dev_guild))
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            log.info("Đã sync lệnh vào server test %s", dev_guild)
        else:
            await self.tree.sync()
            log.info("Đã sync lệnh global")

    async def on_ready(self):
        log.info("Đăng nhập: %s (id=%s)", self.user, self.user.id)
        await self.change_presence(activity=discord.Game("/help | học Python"))

    async def on_app_command_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        if isinstance(error, app_commands.MissingPermissions):
            msg = "Bạn không có quyền dùng lệnh này."
        elif isinstance(error, app_commands.BotMissingPermissions):
            msg = "Bot thiếu quyền để làm việc này, hãy cấp thêm quyền cho bot."
        elif isinstance(error, app_commands.CommandOnCooldown):
            msg = f"Từ từ thôi, thử lại sau {error.retry_after:.0f}s."
        elif isinstance(error, app_commands.NoPrivateMessage):
            msg = "Lệnh này chỉ dùng được trong server."
        else:
            log.exception("Lỗi lệnh chưa xử lý", exc_info=error)
            msg = "Có lỗi xảy ra, thử lại sau nhé."

        if interaction.response.is_done():
            await interaction.followup.send(msg, ephemeral=True)
        else:
            await interaction.response.send_message(msg, ephemeral=True)

    async def close(self):
        await self.db.close()
        await super().close()


async def main():
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise SystemExit("Thiếu DISCORD_TOKEN trong file .env")
    async with LunariLike() as bot:
        await bot.start(token)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
