from datetime import timedelta

import discord
from discord import app_commands
from discord.ext import commands


def can_act_on(interaction: discord.Interaction, target: discord.Member) -> str | None:
    """Trả về chuỗi lỗi nếu không được phép thao tác, None nếu OK."""
    guild = interaction.guild
    user = interaction.user
    if target == user:
        return "Bạn không thể tự xử lý chính mình."
    if target == guild.owner:
        return "Không thể xử lý chủ server."
    if target == guild.me:
        return "Đừng bắt bot tự kick mình chứ :v"
    if user != guild.owner and target.top_role >= user.top_role:
        return "Role của người đó cao hơn hoặc bằng bạn."
    if target.top_role >= guild.me.top_role:
        return "Role của người đó cao hơn hoặc bằng bot."
    return None


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="kick", description="Kick một thành viên")
    @app_commands.describe(member="Người cần kick", reason="Lý do")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(kick_members=True)
    @app_commands.checks.bot_has_permissions(kick_members=True)
    async def kick(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str = "Không có lý do",
    ):
        if err := can_act_on(interaction, member):
            return await interaction.response.send_message(err, ephemeral=True)
        await member.kick(reason=f"{interaction.user}: {reason}")
        await interaction.response.send_message(f"Đã kick **{member}**. Lý do: {reason}")

    @app_commands.command(name="ban", description="Ban một thành viên")
    @app_commands.describe(member="Người cần ban", reason="Lý do")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.checks.bot_has_permissions(ban_members=True)
    async def ban(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str = "Không có lý do",
    ):
        if err := can_act_on(interaction, member):
            return await interaction.response.send_message(err, ephemeral=True)
        await member.ban(reason=f"{interaction.user}: {reason}")
        await interaction.response.send_message(f"Đã ban **{member}**. Lý do: {reason}")

    @app_commands.command(name="timeout", description="Mute (timeout) một thành viên")
    @app_commands.describe(member="Người cần timeout", minutes="Số phút (1-40320)", reason="Lý do")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(moderate_members=True)
    @app_commands.checks.bot_has_permissions(moderate_members=True)
    async def timeout(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        minutes: app_commands.Range[int, 1, 40320],
        reason: str = "Không có lý do",
    ):
        if err := can_act_on(interaction, member):
            return await interaction.response.send_message(err, ephemeral=True)
        await member.timeout(timedelta(minutes=minutes), reason=f"{interaction.user}: {reason}")
        await interaction.response.send_message(
            f"Đã timeout **{member}** trong {minutes} phút. Lý do: {reason}"
        )

    @app_commands.command(name="clear", description="Xoá tin nhắn gần nhất trong kênh")
    @app_commands.describe(amount="Số tin nhắn cần xoá (1-100)")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.checks.bot_has_permissions(manage_messages=True, read_message_history=True)
    async def clear(
        self,
        interaction: discord.Interaction,
        amount: app_commands.Range[int, 1, 100],
    ):
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"Đã xoá {len(deleted)} tin nhắn.", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))
