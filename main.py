import discord
from discord.ext import commands
import os
import datetime
from datetime import date

intents = discord.Intents.all()
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Create the folder structure if it doesn't exist
    channel_folder = f"logs/{message.channel.name}"
    if not os.path.exists(channel_folder):
        os.makedirs(channel_folder)

    # Get the current date
    today = date.today()
    log_file = f"{channel_folder}/{today}.txt"

    # Log the message
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{message.created_at}] {message.author}: {message.content}\n")

    await bot.process_commands(message)

@bot.event
async def on_message_edit(before, after):
    if before.author == bot.user:
        return

    # Create the folder structure if it doesn't exist
    channel_folder = f"logs/{before.channel.name}"
    if not os.path.exists(channel_folder):
        os.makedirs(channel_folder)

    # Get the current date
    today = date.today()
    log_file = f"{channel_folder}/{today}.txt"

    # Log the message edit
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{before.created_at}] {before.author} edited message: {before.content} -> {after.content}\n")

@bot.event
async def on_message_delete(message):
    if message.author == bot.user:
        return

    # Create the folder structure if it doesn't exist
    channel_folder = f"logs/{message.channel.name}"
    if not os.path.exists(channel_folder):
        os.makedirs(channel_folder)

    # Get the current date
    today = date.today()
    log_file = f"{channel_folder}/{today}.txt"

    # Log the message deletion
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{message.created_at}] {message.author} deleted message: {message.content}\n")

log_channel_id = 1234567890  # Replace with your log channel ID

@bot.event
async def on_ready():
    global log_channel
    log_channel = bot.get_channel(log_channel_id)
    print(f'Logged in as {bot.user.name}')

@bot.command()
@commands.has_permissions(administrator=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    embed = discord.Embed(title="Moderation Log", color=0xFF0000)
    embed.add_field(name="Action", value="Ban", inline=False)
    embed.add_field(name="User", value=member.mention, inline=False)
    embed.add_field(name="Moderator", value=ctx.author.mention, inline=False)
    if reason:
        embed.add_field(name="Reason", value=reason, inline=False)
    await log_channel.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')

    for ban in banned_users:
        user = ban.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            embed = discord.Embed(title="Moderation Log", color=0xFF0000)
            embed.add_field(name="Action", value="Unban", inline=False)
            embed.add_field(name="User", value=user.mention, inline=False)
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=False)
            await log_channel.send(embed=embed)
            return

@bot.command()
@commands.has_permissions(administrator=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    embed = discord.Embed(title="Moderation Log", color=0xFF0000)
    embed.add_field(name="Action", value="Kick", inline=False)
    embed.add_field(name="User", value=member.mention, inline=False)
    embed.add_field(name="Moderator", value=ctx.author.mention, inline=False)
    if reason:
        embed.add_field(name="Reason", value=reason, inline=False)
    await log_channel.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def timeout(ctx, member: discord.Member, seconds: int, *, reason=None):
    await member.timeout(discord.utils.parse_time(f"{seconds}s"), reason=reason)
    embed = discord.Embed(title="Moderation Log", color=0xFF0000)
    embed.add_field(name="Action", value="Timeout", inline=False)
    embed.add_field(name="User", value=member.mention, inline=False)
    embed.add_field(name="Moderator", value=ctx.author.mention, inline=False)
    if reason:
        embed.add_field(name="Reason", value=reason, inline=False)
    await log_channel.send(embed=embed)

bot.run('YOUR_BOT_TOKEN')
