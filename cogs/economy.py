import random
import time

import discord
from discord import app_commands
from discord.ext import commands

DAILY_REWARD = 500
DAILY_COOLDOWN = 24 * 3600
WORK_COOLDOWN = 3600
CURRENCY = "xu"


class Economy(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = bot.db

    @app_commands.command(name="balance", description="Xem số dư")
    @app_commands.describe(user="Người cần xem (mặc định là bạn)")
    async def balance(self, interaction: discord.Interaction, user: discord.User | None = None):
        user = user or interaction.user
        bal = await self.db.get_balance(user.id)
        await interaction.response.send_message(f"**{user.display_name}** có **{bal:,}** {CURRENCY}.")

    @app_commands.command(name="daily", description="Nhận thưởng mỗi ngày")
    async def daily(self, interaction: discord.Interaction):
        uid = interaction.user.id
        now = time.time()
        last = await self.db.get_cooldown(uid, "last_daily")
        if now - last < DAILY_COOLDOWN:
            ready = int(last + DAILY_COOLDOWN)
            return await interaction.response.send_message(
                f"Bạn đã nhận rồi, nhận lại <t:{ready}:R>.", ephemeral=True
            )
        await self.db.set_cooldown(uid, "last_daily", now)
        bal = await self.db.add_balance(uid, DAILY_REWARD)
        await interaction.response.send_message(
            f"Nhận **{DAILY_REWARD:,}** {CURRENCY}! Số dư: **{bal:,}**."
        )

    @app_commands.command(name="work", description="Đi làm kiếm xu (1 giờ/lần)")
    async def work(self, interaction: discord.Interaction):
        uid = interaction.user.id
        now = time.time()
        last = await self.db.get_cooldown(uid, "last_work")
        if now - last < WORK_COOLDOWN:
            ready = int(last + WORK_COOLDOWN)
            return await interaction.response.send_message(
                f"Bạn đang mệt, làm tiếp <t:{ready}:R>.", ephemeral=True
            )
        earned = random.randint(50, 150)
        job = random.choice(["code dạo", "giao hàng", "bán trà sữa", "sửa máy tính", "dạy kèm"])
        await self.db.set_cooldown(uid, "last_work", now)
        bal = await self.db.add_balance(uid, earned)
        await interaction.response.send_message(
            f"Bạn đi **{job}** và kiếm được **{earned}** {CURRENCY}. Số dư: **{bal:,}**."
        )

    @app_commands.command(name="give", description="Chuyển xu cho người khác")
    @app_commands.describe(user="Người nhận", amount="Số xu")
    async def give(
        self,
        interaction: discord.Interaction,
        user: discord.User,
        amount: app_commands.Range[int, 1, 1_000_000_000],
    ):
        if user.bot or user.id == interaction.user.id:
            return await interaction.response.send_message(
                "Không thể chuyển cho bot hoặc chính bạn.", ephemeral=True
            )
        ok = await self.db.transfer(interaction.user.id, user.id, amount)
        if not ok:
            return await interaction.response.send_message("Bạn không đủ xu.", ephemeral=True)
        await interaction.response.send_message(
            f"Đã chuyển **{amount:,}** {CURRENCY} cho {user.mention}."
        )

    @app_commands.command(name="leaderboard", description="Top người giàu nhất")
    async def leaderboard(self, interaction: discord.Interaction):
        rows = await self.db.leaderboard(10)
        if not rows:
            return await interaction.response.send_message("Chưa có ai trong bảng xếp hạng.")
        lines = [
            f"**{i}.** <@{uid}> — {bal:,} {CURRENCY}"
            for i, (uid, bal) in enumerate(rows, start=1)
        ]
        embed = discord.Embed(
            title="Bảng xếp hạng",
            description="\n".join(lines),
            color=discord.Color.purple(),
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Economy(bot))
