import discord
from discord.ext import commands

AUTO_ROLE_ID = 1422154357155303434  # Role to give automatically

class AutoRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        role = member.guild.get_role(AUTO_ROLE_ID)
        if role:
            try:
                await member.add_roles(role)
                print(f"✅ Added auto-role to {member}")
            except discord.Forbidden:
                print(f"⚠️ Cannot add role to {member} (missing permissions)")
        else:
            print(f"⚠️ Role ID {AUTO_ROLE_ID} not found in {member.guild.name}")

# ---------------- SETUP ----------------
async def setup(bot):
    await bot.add_cog(AutoRole(bot))
