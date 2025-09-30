# cogs/presence.py
import discord
from discord.ext import commands, tasks
import asyncio

class Presence(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.presence_task = None  # We'll create the task later

    @commands.Cog.listener()
    async def on_ready(self):
        # Only start the task once
        if self.presence_task is None:
            self.presence_task = self.bot.loop.create_task(self.change_presence_loop())
            print("Presence: True")  # Task successfully started

    async def change_presence_loop(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            try:
                # Playing
                await self.bot.change_presence(activity=discord.Game(name="play.lunarmc.fun"))
                await asyncio.sleep(10)

                # Watching
                total_players = sum(guild.member_count for guild in self.bot.guilds)
                await self.bot.change_presence(activity=discord.Activity(
                    type=discord.ActivityType.watching,
                    name=f"{total_players} players in Lunar MC"
                ))
                await asyncio.sleep(10)
            except Exception as e:
                print(f"Presence update failed: {e}")
                await asyncio.sleep(10)  # Wait before retrying

async def setup(bot):
    await bot.add_cog(Presence(bot))
