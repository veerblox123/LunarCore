import discord
from discord.ext import commands
from discord.ui import View, Select, Button
import io

# -----------------------------
# CONFIG (replace IDs with yours)
TICKET_CATEGORY_ID = 123456789012345678  # your tickets category ID
LOG_CHANNEL_ID = 123456789012345678      # your log channel ID
OWNER_ROLE_ID = 123456789012345678       # your owner role ID
# -----------------------------


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
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True),
            guild.get_role(OWNER_ROLE_ID): discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }

        ticket_channel = await guild.create_text_channel(
            f"ticket-{interaction.user.name}",
            category=category,
            overwrites=overwrites
        )

        # Auto ping user + owner role
        embed = discord.Embed(
            title="🎫 Ticket Created",
            description=f"Hello {interaction.user.mention}, a staff member will be with you shortly.\n\n"
                        f"**Ticket Type:** {self.values[0]}",
            color=discord.Color.blue()
        )

        view = TicketButtons(ticket_channel, interaction.user)
        await ticket_channel.send(content=f"{interaction.user.mention} <@&{OWNER_ROLE_ID}>", embed=embed, view=view)

        await interaction.response.send_message(f"✅ Ticket created: {ticket_channel.mention}", ephemeral=True)


class TicketButtons(View):
    def __init__(self, channel, author):
        super().__init__(timeout=None)
        self.channel = channel
        self.author = author

    @discord.ui.button(label="✅ Claim", style=discord.ButtonStyle.green)
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.channel.send(f"🔒 Ticket claimed by {interaction.user.mention}")

    @discord.ui.button(label="❌ Close", style=discord.ButtonStyle.red)
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)

        # Create transcript
        messages = [f"[{m.created_at}] {m.author}: {m.content}" async for m in self.channel.history(limit=None, oldest_first=True)]
        transcript = "\n".join(messages) if messages else "No messages found."

        transcript_file = discord.File(io.BytesIO(transcript.encode()), filename=f"transcript-{self.channel.name}.txt")
        await log_channel.send(file=transcript_file)

        await self.channel.delete()

    @discord.ui.button(label="➕ Add Member", style=discord.ButtonStyle.blurple)
    async def add_member(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = AddRemoveMemberModal(self.channel, add=True)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="➖ Remove Member", style=discord.ButtonStyle.gray)
    async def remove_member(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = AddRemoveMemberModal(self.channel, add=False)
        await interaction.response.send_modal(modal)


class AddRemoveMemberModal(discord.ui.Modal):
    def __init__(self, channel, add=True):
        super().__init__(title="Manage Ticket Members")
        self.channel = channel
        self.add = add

        self.user_id = discord.ui.TextInput(label="User ID", placeholder="Enter the user's Discord ID")
        self.add_item(self.user_id)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            user = await interaction.guild.fetch_member(int(self.user_id.value))
        except:
            await interaction.response.send_message("❌ Invalid user ID.", ephemeral=True)
            return

        if self.add:
            await self.channel.set_permissions(user, view_channel=True, send_messages=True)
            await self.channel.send(f"✅ {user.mention} added to the ticket.")
        else:
            await self.channel.set_permissions(user, overwrite=None)
            await self.channel.send(f"❌ {user.mention} removed from the ticket.")

        await interaction.response.send_message("✅ Done!", ephemeral=True)


class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketDropdown())


class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def setup_ticket(self, ctx):
        embed = discord.Embed(
            title="🎫 Support Tickets",
            description="Select the type of ticket you want to create:",
            color=discord.Color.gold()
        )
        await ctx.send(embed=embed, view=TicketView())


async def setup(bot):
    await bot.add_cog(TicketSystem(bot))
