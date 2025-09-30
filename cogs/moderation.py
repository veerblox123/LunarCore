import discord
from discord.ext import commands
from discord import app_commands
from discord.utils import utcnow
from datetime import timedelta
import re

# ---------------- CONFIG ----------------
MOD_LOG_CHANNEL_ID = 1419969511171297311  # Your mod-log channel ID
OWNER_ROLE_ID = 1422154213940662282      # Your Owner role ID
SPAM_THRESHOLD = 3
SPAM_INTERVAL = 3
user_messages = {}
warns = {}

# ---------------- OWNER CHECK ----------------
def is_owner():
    async def predicate(ctx_or_interaction):
        if isinstance(ctx_or_interaction, commands.Context):  # Prefix
            return OWNER_ROLE_ID in [role.id for role in ctx_or_interaction.author.roles]
        elif isinstance(ctx_or_interaction, discord.Interaction):  # Slash
            member = ctx_or_interaction.user
            return OWNER_ROLE_ID in [role.id for role in member.roles]
        return False
    return commands.check(predicate)

# ---------------- MODERATION COG ----------------
class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ---------------- PREFIX COMMANDS ----------------
    @commands.command(name="kick")
    @is_owner()
    async def kick_prefix(self, ctx, member: discord.Member, *, reason="No reason provided"):
        if ctx.author.top_role <= member.top_role:
            return await ctx.send("⚠️ Cannot kick a member with equal/higher role.")
        try:
            await member.kick(reason=reason)
            await ctx.send(f"👢 {member.mention} kicked. Reason: {reason}")
            await self.log_action(ctx.guild, f"Kicked {member} | Reason: {reason}")
        except discord.Forbidden:
            await ctx.send("⚠️ Missing permissions to kick this member.")

    @commands.command(name="ban")
    @is_owner()
    async def ban_prefix(self, ctx, member: discord.Member, *, reason="No reason provided"):
        if ctx.author.top_role <= member.top_role:
            return await ctx.send("⚠️ Cannot ban a member with equal/higher role.")
        try:
            await member.ban(reason=reason)
            await ctx.send(f"🔨 {member.mention} banned. Reason: {reason}")
            await self.log_action(ctx.guild, f"Banned {member} | Reason: {reason}")
        except discord.Forbidden:
            await ctx.send("⚠️ Missing permissions to ban this member.")

    @commands.command(name="timeout")
    @is_owner()
    async def timeout_prefix(self, ctx, member: discord.Member, minutes: int):
        if ctx.author.top_role <= member.top_role:
            return await ctx.send("⚠️ Cannot timeout a member with equal/higher role.")
        try:
            await member.edit(timed_out_until=utcnow() + timedelta(minutes=minutes))
            await ctx.send(f"⏳ {member.mention} timed out for {minutes} minutes.")
            await self.log_action(ctx.guild, f"Timed out {member} for {minutes} minutes")
        except discord.Forbidden:
            await ctx.send("⚠️ Missing permissions to timeout.")

    @commands.command(name="mute")
    @is_owner()
    async def mute_prefix(self, ctx, member: discord.Member, minutes: int):
        if ctx.author.top_role <= member.top_role:
            return await ctx.send("⚠️ Cannot mute a member with equal/higher role.")
        try:
            await member.edit(timed_out_until=utcnow() + timedelta(minutes=minutes))
            await ctx.send(f"🔇 {member.mention} muted for {minutes} minutes.")
            await self.log_action(ctx.guild, f"Muted {member} for {minutes} minutes")
        except discord.Forbidden:
            await ctx.send("⚠️ Missing permissions to mute.")

    @commands.command(name="unmute")
    @is_owner()
    async def unmute_prefix(self, ctx, member: discord.Member):
        try:
            await member.edit(timed_out_until=None)
            await ctx.send(f"🔊 {member.mention} unmuted.")
            await self.log_action(ctx.guild, f"Unmuted {member}")
        except discord.Forbidden:
            await ctx.send("⚠️ Missing permissions to unmute.")

    @commands.command(name="warn")
    @is_owner()
    async def warn_prefix(self, ctx, member: discord.Member, *, reason="No reason provided"):
        warns.setdefault(member.id, [])
        warns[member.id].append(reason)
        await ctx.send(f"⚠️ {member.mention} warned. Reason: {reason}")
        await self.log_action(ctx.guild, f"Warned {member} | Reason: {reason}")

    @commands.command(name="purge")
    @is_owner()
    async def purge_prefix(self, ctx, amount: int):
        deleted = await ctx.channel.purge(limit=amount)
        await ctx.send(f"🧹 Deleted {len(deleted)} messages.", delete_after=5)
        await self.log_action(ctx.guild, f"Purged {len(deleted)} messages in {ctx.channel}")

    @commands.command(name="lock")
    @is_owner()
    async def lock_prefix(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.send("🔒 Channel locked.")
        await self.log_action(ctx.guild, f"Locked channel {ctx.channel}")

    @commands.command(name="unlock")
    @is_owner()
    async def unlock_prefix(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
        await ctx.send("🔓 Channel unlocked.")
        await self.log_action(ctx.guild, f"Unlocked channel {ctx.channel}")

    # ---------------- SLASH COMMANDS ----------------
    @app_commands.command(name="kick", description="Kick a member")
    @is_owner()
    async def kick_slash(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        if interaction.user.top_role <= member.top_role:
            return await interaction.response.send_message("⚠️ Cannot kick this member.", ephemeral=True)
        try:
            await member.kick(reason=reason)
            await interaction.response.send_message(f"👢 {member.mention} kicked. Reason: {reason}")
            await self.log_action(interaction.guild, f"Kicked {member} | Reason: {reason}")
        except discord.Forbidden:
            await interaction.response.send_message("⚠️ Missing permissions.", ephemeral=True)

    @app_commands.command(name="ban", description="Ban a member")
    @is_owner()
    async def ban_slash(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        if interaction.user.top_role <= member.top_role:
            return await interaction.response.send_message("⚠️ Cannot ban this member.", ephemeral=True)
        try:
            await member.ban(reason=reason)
            await interaction.response.send_message(f"🔨 {member.mention} banned. Reason: {reason}")
            await self.log_action(interaction.guild, f"Banned {member} | Reason: {reason}")
        except discord.Forbidden:
            await interaction.response.send_message("⚠️ Missing permissions.", ephemeral=True)

    @app_commands.command(name="timeout", description="Timeout a member")
    @is_owner()
    async def timeout_slash(self, interaction: discord.Interaction, member: discord.Member, minutes: int):
        if interaction.user.top_role <= member.top_role:
            return await interaction.response.send_message("⚠️ Cannot timeout this member.", ephemeral=True)
        try:
            await member.edit(timed_out_until=utcnow() + timedelta(minutes=minutes))
            await interaction.response.send_message(f"⏳ {member.mention} timed out for {minutes} minutes.")
            await self.log_action(interaction.guild, f"Timed out {member} for {minutes} minutes")
        except discord.Forbidden:
            await interaction.response.send_message("⚠️ Missing permissions.", ephemeral=True)

    @app_commands.command(name="mute", description="Mute a member")
    @is_owner()
    async def mute_slash(self, interaction: discord.Interaction, member: discord.Member, minutes: int):
        if interaction.user.top_role <= member.top_role:
            return await interaction.response.send_message("⚠️ Cannot mute this member.", ephemeral=True)
        try:
            await member.edit(timed_out_until=utcnow() + timedelta(minutes=minutes))
            await interaction.response.send_message(f"🔇 {member.mention} muted for {minutes} minutes.")
            await self.log_action(interaction.guild, f"Muted {member} for {minutes} minutes")
        except discord.Forbidden:
            await interaction.response.send_message("⚠️ Missing permissions.", ephemeral=True)

    @app_commands.command(name="unmute", description="Unmute a member")
    @is_owner()
    async def unmute_slash(self, interaction: discord.Interaction, member: discord.Member):
        try:
            await member.edit(timed_out_until=None)
            await interaction.response.send_message(f"🔊 {member.mention} unmuted.")
            await self.log_action(interaction.guild, f"Unmuted {member}")
        except discord.Forbidden:
            await interaction.response.send_message("⚠️ Missing permissions.", ephemeral=True)

    @app_commands.command(name="warn", description="Warn a member")
    @is_owner()
    async def warn_slash(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        warns.setdefault(member.id, [])
        warns[member.id].append(reason)
        await interaction.response.send_message(f"⚠️ {member.mention} warned. Reason: {reason}")
        await self.log_action(interaction.guild, f"Warned {member} | Reason: {reason}")

    @app_commands.command(name="purge", description="Purge messages")
    @is_owner()
    async def purge_slash(self, interaction: discord.Interaction, amount: int):
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.response.send_message(f"🧹 Deleted {len(deleted)} messages.", ephemeral=True)
        await self.log_action(interaction.guild, f"Purged {len(deleted)} messages in {interaction.channel}")

    @app_commands.command(name="lock", description="Lock channel")
    @is_owner()
    async def lock_slash(self, interaction: discord.Interaction):
        await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
        await interaction.response.send_message("🔒 Channel locked.", ephemeral=True)
        await self.log_action(interaction.guild, f"Locked channel {interaction.channel}")

    @app_commands.command(name="unlock", description="Unlock channel")
    @is_owner()
    async def unlock_slash(self, interaction: discord.Interaction):
        await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=True)
        await interaction.response.send_message("🔓 Channel unlocked.", ephemeral=True)
        await self.log_action(interaction.guild, f"Unlocked channel {interaction.channel}")

    # ---------------- LOGGING ----------------
    async def log_action(self, guild, message):
        channel = guild.get_channel(MOD_LOG_CHANNEL_ID)
        if channel:
            await channel.send(f"🛡️ {message}")

    # ---------------- AUTO-MODERATION ----------------
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # Anti-spam
        now = utcnow()
        msgs = user_messages.get(message.author.id, [])
        msgs = [t for t in msgs if (now - t).total_seconds() < SPAM_INTERVAL]
        msgs.append(now)
        user_messages[message.author.id] = msgs
        if len(msgs) > SPAM_THRESHOLD:
            await message.delete()
            await message.channel.send(f"⚠️ {message.author.mention}, stop spamming!", delete_after=5)

        # Anti-link
        if re.search(r"(https?://|discord\.gg/|discordapp\.com/invite/)", message.content):
            await message.delete()
            await message.channel.send(f"⚠️ {message.author.mention}, links are not allowed!", delete_after=5)

        # Caps lock filter
        if len(message.content) >= 10 and message.content.isupper():
            await message.channel.send(f"⚠️ {message.author.mention}, no caps lock spam!", delete_after=5)

# ---------------- SETUP ----------------
async def setup(bot):
    await bot.add_cog(Moderation(bot))
