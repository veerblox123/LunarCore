import discord
from discord.ext import commands

class Greetings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Auto greet new members
    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = self.bot.get_channel(1419969511171297311)  # Updated welcome channel ID
        if channel:
            embed = discord.Embed(
                title="Welcome!",
                description=f"👋 {member.mention}, welcome to **{member.guild.name}**! Enjoy your stay 🎉",
                color=discord.Color.blurple()
            )
            await channel.send(embed=embed)

    # Optional: Prefix greet command
    @commands.command(name="greet")
    async def greet_prefix(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        await ctx.send(f"👋 Hello {member.mention}, welcome!")

async def setup(bot):
    await bot.add_cog(Greetings(bot))
