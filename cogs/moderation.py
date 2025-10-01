import discord
from discord.ext import commands

OWNER_ROLE_ID = OWNER OR STAFF ID # only this role can use moderation

def is_owner_role():
    async def predicate(ctx):
        return ctx.guild.get_role(OWNER_ROLE_ID) in ctx.author.roles
    return commands.check(predicate)

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @is_owner_role()
    async def kick(self, ctx, member: discord.Member, *, reason="No reason provided"):
        await member.kick(reason=reason)
        await ctx.send(f"✅ {member} kicked. Reason: {reason}")

    @commands.command()
    @is_owner_role()
    async def ban(self, ctx, member: discord.Member, *, reason="No reason provided"):
        await member.ban(reason=reason)
        await ctx.send(f"✅ {member} banned. Reason: {reason}")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
