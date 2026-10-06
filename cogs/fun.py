import random
import time

import discord
from discord import app_commands
from discord.ext import commands

EIGHT_BALL = [
    "Chắc chắn rồi.", "Có vẻ ổn đấy.", "Hỏi lại sau nhé.",
    "Đừng trông chờ vào nó.", "Khả năng cao là không.", "Làm đi, sợ gì!",
]


class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Xem độ trễ của bot")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Pong! {self.bot.latency * 1000:.0f}ms")

    @app_commands.command(name="coinflip", description="Tung đồng xu")
    async def coinflip(self, interaction: discord.Interaction):
        await interaction.response.send_message(random.choice(["Sấp", "Ngửa"]))

    @app_commands.command(name="8ball", description="Hỏi quả cầu thần kỳ")
    @app_commands.describe(question="Câu hỏi của bạn")
    async def eight_ball(self, interaction: discord.Interaction, question: str):
        await interaction.response.send_message(f"**{question}**\n{random.choice(EIGHT_BALL)}")

    @app_commands.command(name="avatar", description="Xem avatar")
    @app_commands.describe(user="Người cần xem (mặc định là bạn)")
    async def avatar(self, interaction: discord.Interaction, user: discord.User | None = None):
        user = user or interaction.user
        embed = discord.Embed(title=f"Avatar của {user.display_name}", color=discord.Color.purple())
        embed.set_image(url=user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="userinfo", description="Thông tin người dùng")
    @app_commands.describe(user="Người cần xem (mặc định là bạn)")
    async def userinfo(self, interaction: discord.Interaction, user: discord.User | None = None):
        user = user or interaction.user
        embed = discord.Embed(title=str(user), color=discord.Color.purple())
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="ID", value=user.id)
        embed.add_field(name="Tạo tài khoản", value=discord.utils.format_dt(user.created_at, "R"))
        if isinstance(user, discord.Member) and user.joined_at:
            embed.add_field(name="Vào server", value=discord.utils.format_dt(user.joined_at, "R"))
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Fun(bot))
