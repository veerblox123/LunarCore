import discord
from discord.ext import commands
from discord.ui import View, Select, Button
import io

TICKET_CATEGORY_ID = check README.md  # category for tickets
LOG_CHANNEL_ID = check README.md      # log channel
OWNER_ROLE_ID = check README.md       # staff/owner role
TICKET_PANEL_CHANNEL_ID = check README.md  # channel for ticket panel

class TicketDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="📦 Purchase Support", value="purchase"),
            discord.SelectOption(label="🎮 Gameplay Help", value="gameplay"),
            discord.SelectOption(label="⚡ Staff Help", value="staff"),
            discord.SelectOption(label="❓ General Query", value="general"),
        ]
        super().__init__(placeholder="Select a ticket type...", options=options)

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        category = guild.get_channel(TICKET_CATEGORY_ID)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.get_role(OWNER_ROLE_ID): discord.PermissionOverwrite(view_channel=True, send_messages=True),
        }

        ticket_channel = await guild.create_text_channel(
            f"ticket-{interaction.user.name}",
            category=category,
            overwrites=overwrites
        )

        embed = discord.Embed(
            title="🎫 Ticket Created",
            description=f"{interaction.user.mention}, thanks for opening a ticket!\nType: `{self.values[0]}`",
            color=discord.Color.blue()
        )

        view = TicketButtons(ticket_channel)
        await ticket_channel.send(content=f"{interaction.user.mention} <@&{OWNER_ROLE_ID}>", embed=embed, view=view)
        await interaction.response.send_message(f"✅ Ticket created: {ticket_channel.mention}", ephemeral=True)

class TicketButtons(View):
    def __init__(self, channel):
        super().__init__(timeout=None)
        self.channel = channel

    @discord.ui.button(label="✅ Claim", style=discord.ButtonStyle.green)
    async def claim(self, interaction: discord.Interaction, button: Button):
        await self.channel.send(f"🔒 Ticket claimed by {interaction.user.mention}")

    @discord.ui.button(label="❌ Close", style=discord.ButtonStyle.red)
    async def close(self, interaction: discord.Interaction, button: Button):
        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        transcript = [f"[{m.created_at}] {m.author}: {m.content}" async for m in self.channel.history(limit=None, oldest_first=True)]
        transcript_text = "\n".join(transcript) if transcript else "No messages found."
        file = discord.File(io.BytesIO(transcript_text.encode()), filename=f"{self.channel.name}-transcript.txt")
        await log_channel.send(file=file)
        await self.channel.delete()

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketDropdown())

class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        channel = self.bot.get_channel(TICKET_PANEL_CHANNEL_ID)
        if channel:
            async for msg in channel.history(limit=5):
                if msg.author == self.bot.user:
                    await msg.delete()
            embed = discord.Embed(
                title="🎫 Support Tickets",
                description="Choose a ticket type below 👇",
                color=discord.Color.gold()
            )
            await channel.send(embed=embed, view=TicketView())
            print("✅ Ticket system initialized")

async def setup(bot):
    await bot.add_cog(TicketSystem(bot))
