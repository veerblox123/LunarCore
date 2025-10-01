import discord
from discord.ext import commands, tasks
import asyncio

class Presence(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.status_task.start()

    @tasks.loop(seconds=10)
    async def status_task(self):
        await self.bot.change_presence(activity=discord.Game("play.lunarmc.fun"))
        await asyncio.sleep(10)
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="players in Lunar MC"))

async def setup(bot):
    await bot.add_cog(Presence(bot))
