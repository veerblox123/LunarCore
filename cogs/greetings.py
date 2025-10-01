import discord
from discord.ext import commands

WELCOME_CHANNEL_ID = CHANNEL_ID_FOR_WLCM_MSGS  # replace with your welcome channel ID

class Greetings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel = self.bot.get_channel(WELCOME_CHANNEL_ID)
        if channel:
            embed = discord.Embed(
                title="🌟 Welcome Adventurer!",
                description=(
                    f"**{member.name}**\n"
                    f"Hey adventurer 👋, we’re glad you joined our community! ✨\n\n"
                    f"🚀 Explore, build, and survive in a world full of fun and adventure.\n"
                    f"💎 Be sure to read the rules and check out the updates.\n"
                    f"🎉 Don’t forget to say hi — we’re a friendly bunch!\n"
                    f"👉 Your journey under the stars begins now… 🌌"
                ),
                color=discord.Color.green()
            )
            # Add your GIF
            embed.set_image(url="https://media.discordapp.net/attachments/1421195599528726532/1421251340088377515/Black_and_White_Modern_Welcome_to_my_Channel_Video-VEED.gif?ex=68dda0f5&is=68dc4f75&hm=9403339d8370a71069b4847ed5c69a75fe8dd3d7c373cb5323edf84cd4cb865f&=")

            await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Greetings(bot))
