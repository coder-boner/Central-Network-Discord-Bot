#MADE BY Coder-Boner (https://github.com/coder-boner/)
#Repo (https://github.com/coder-boner/Central-Network-Discord-Bot)

import os
import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta

# Replace with your bot token and target moderation logs channel ID
BOT_TOKEN = "BOT_TOKEN"
MOD_LOG_CHANNEL_ID = 123456789012345678

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.guild_messages = True
intents.bans = True
intents.moderation = True
intents.members = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="/", intents=intents)

    async def setup_hook(self):
        # Sync commands to the server
        await self.tree.sync()

bot = MyBot()

# Create a folder for storing logs
LOGS_DIR = "logs"
os.makedirs(LOGS_DIR, exist_ok=True)

@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}")

    async def setup_hook(self):
        await self.tree.sync()
        print("Commands synced successfully!")


# Utility function to write messages to a log file
def write_to_log(channel_name, date, content):
    channel_dir = os.path.join(LOGS_DIR, channel_name)
    os.makedirs(channel_dir, exist_ok=True)
    log_file_path = os.path.join(channel_dir, f"{date}.txt")
    with open(log_file_path, "a", encoding="utf-8") as log_file:
        log_file.write(content + "\n")

# Log messages
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    channel_name = message.channel.name
    date = datetime.now().strftime("%Y-%m-%d")
    log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] {message.author}: {message.content}"
    write_to_log(channel_name, date, log_entry)

# Log deleted messages
@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return

    channel_name = message.channel.name
    date = datetime.now().strftime("%Y-%m-%d")
    log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] {message.author}: MESSAGE DELETED: {message.content}"
    write_to_log(channel_name, date, log_entry)

    # Send moderation log
    channel = bot.get_channel(MOD_LOG_CHANNEL_ID)
    if channel:
        await channel.send(f"Message deleted in #{channel_name} by {message.author}: {message.content}")

# Log member bans
@bot.event
async def on_member_ban(guild, user):
    log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] {user} was banned."
    write_to_log("moderation", datetime.now().strftime("%Y-%m-%d"), log_entry)

    # Send moderation log
    channel = bot.get_channel(MOD_LOG_CHANNEL_ID)
    if channel:
        await channel.send(log_entry)

# Log member unbans
@bot.event
async def on_member_unban(guild, user):
    log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] {user} was unbanned."
    write_to_log("moderation", datetime.now().strftime("%Y-%m-%d"), log_entry)

    # Send moderation log
    channel = bot.get_channel(MOD_LOG_CHANNEL_ID)
    if channel:
        await channel.send(log_entry)

# Log member kicks (requires integration with audit logs)
@bot.event
async def on_member_remove(member):
    guild = member.guild
    async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.kick):
        if entry.target == member:
            log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] {member} was kicked by {entry.user}."
            write_to_log("moderation", datetime.now().strftime("%Y-%m-%d"), log_entry)

            # Send moderation log
            channel = bot.get_channel(MOD_LOG_CHANNEL_ID)
            if channel:
                await channel.send(log_entry)

# Moderation commands
@bot.tree.command(name="kick", description="Kick a member from the server")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    await member.kick(reason=reason)
    log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] {member} was kicked by {interaction.user} for: {reason}"
    write_to_log("moderation", datetime.now().strftime("%Y-%m-%d"), log_entry)

    # Send moderation log
    channel = bot.get_channel(MOD_LOG_CHANNEL_ID)
    if channel:
        await channel.send(log_entry)
    await interaction.response.send_message(f"{member} has been kicked.")

@bot.tree.command(name="ban", description="Ban a member from the server")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    await member.ban(reason=reason)
    log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] {member} was banned by {interaction.user} for: {reason}"
    write_to_log("moderation", datetime.now().strftime("%Y-%m-%d"), log_entry)

    # Send moderation log
    channel = bot.get_channel(MOD_LOG_CHANNEL_ID)
    if channel:
        await channel.send(log_entry)
    await interaction.response.send_message(f"{member} has been banned.")

@bot.tree.command(name="unban", description="Unban a member from the server")
async def unban(interaction: discord.Interaction, user: discord.User):
    guild = interaction.guild
    await guild.unban(user)
    log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] {user} was unbanned by {interaction.user}."
    write_to_log("moderation", datetime.now().strftime("%Y-%m-%d"), log_entry)

    # Send moderation log
    channel = bot.get_channel(MOD_LOG_CHANNEL_ID)
    if channel:
        await channel.send(log_entry)
    await interaction.response.send_message(f"{user} has been unbanned.")

@bot.tree.command(name="timeout", description="Timeout a member")
async def timeout(interaction: discord.Interaction, member: discord.Member, duration: int, reason: str = "No reason provided"):
    if not interaction.guild.me.guild_permissions.moderate_members:
        await interaction.response.send_message(
            "I do not have permission to timeout members.", ephemeral=True
        )
        return

    until = discord.utils.utcnow() + timedelta(seconds=duration)
    try:
        await member.timeout(until, reason=reason)
        log_entry = (
            f"[{datetime.now().strftime('%H:%M:%S')}] {member} was timed out by "
            f"{interaction.user} for {duration} seconds: {reason}"
        )
        write_to_log("moderation", datetime.now().strftime("%Y-%m-%d"), log_entry)

        # Send moderation log
        channel = bot.get_channel(MOD_LOG_CHANNEL_ID)
        if channel:
            await channel.send(log_entry)

        await interaction.response.send_message(f"{member} has been timed out for {duration} seconds.")
    except Exception as e:
        await interaction.response.send_message(
            f"Failed to timeout {member}: {str(e)}", ephemeral=True
        )


@bot.tree.command(name="remove_timeout", description="Remove a member's timeout")
async def remove_timeout(interaction: discord.Interaction, member: discord.Member):
    await member.timeout(None)
    log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] {member}'s timeout was removed by {interaction.user}."
    write_to_log("moderation", datetime.now().strftime("%Y-%m-%d"), log_entry)

    # Send moderation log
    channel = bot.get_channel(MOD_LOG_CHANNEL_ID)
    if channel:
        await channel.send(log_entry)
    await interaction.response.send_message(f"{member}'s timeout has been removed.")

bot.run(BOT_TOKEN)
