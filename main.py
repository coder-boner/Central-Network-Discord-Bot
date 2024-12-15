import discord
from discord.ext import commands
import logging
import datetime

# Set up logging
logging.basicConfig(filename='moderation.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

# Set up the bot
intents = discord.Intents.default()
intents.members = True
intents.messages = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Event to indicate the bot is ready
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

# Logging channel ID
logging_channel_id = 1234567890  # Replace with your logging channel ID

# Function to log to file and channel
async def log_moderation(action, user, reason=None):
    log_message = f'{action} - {user} - {reason if reason else "No reason provided"}'
    logging.info(log_message)
    logging_channel = bot.get_channel(logging_channel_id)
    if logging_channel:
        await logging_channel.send(log_message)

# Moderation commands
@bot.command(name='ban')
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await log_moderation('Ban', member, reason)

@bot.command(name='kick')
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await log_moderation('Kick', member, reason)

@bot.command(name='mute')
async def mute(ctx, member: discord.Member, *, reason=None):
    # Assuming you have a mute role set up
    mute_role = discord.utils.get(ctx.guild.roles, name='Muted')
    if mute_role:
        await member.add_roles(mute_role, reason=reason)
        await log_moderation('Mute', member, reason)
    else:
        await ctx.send('Mute role not found.')

@bot.command(name='unmute')
async def unmute(ctx, member: discord.Member, *, reason=None):
    # Assuming you have a mute role set up
    mute_role = discord.utils.get(ctx.guild.roles, name='Muted')
    if mute_role:
        await member.remove_roles(mute_role, reason=reason)
        await log_moderation('Unmute', member, reason)
    else:
        await ctx.send('Mute role not found.')

# Message deletion logging
@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return
    log_message = f'Message deleted - {message.author} - {message.content}'
    logging.info(log_message)
    logging_channel = bot.get_channel(logging_channel_id)
    if logging_channel:
        embed = discord.Embed(title='Message Deleted', description=log_message, timestamp=datetime.datetime.now())
        embed.set_author(name=message.author, icon_url=message.author.avatar_url)
        await logging_channel.send(embed=embed)

import json

# Load user data from JSON file
def load_user_data():
    try:
        with open('user_data.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Save user data to JSON file
def save_user_data(data):
    with open('user_data.json', 'w') as file:
        json.dump(data, file)

# Initialize user data if not present
user_data = load_user_data()

# Function to update user levels
def update_user_level(user_id, message):
    global user_data
    if user_id not in user_data:
        user_data[user_id] = {'level': 0, 'experience': 0}
    user_data[user_id]['experience'] += 1  # Adjust experience gain as needed
    if user_data[user_id]['experience'] >= 100:  # Adjust level up threshold as needed
        user_data[user_id]['level'] += 1
        user_data[user_id]['experience'] = 0
        save_user_data(user_data)
        return True
    save_user_data(user_data)
    return False

# Event to track messages and update levels
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if update_user_level(message.author.id, message):
        await message.channel.send(f'Congratulations {message.author.mention}, you leveled up!')
    await bot.process_commands(message)

@bot.event
async def on_message_edit(before, after):
    if before.author.bot:
        return
    log_message = f'Message edited - {before.author} - Before: {before.content} - After: {after.content}'
    logging.info(log_message)
    logging_channel = bot.get_channel(logging_channel_id)
    if logging_channel:
        embed = discord.Embed(title='Message Edited', description=log_message, timestamp=datetime.datetime.now())
        embed.set_author(name=before.author, icon_url=before.author.avatar_url)
        await logging_channel.send(embed=embed)

@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return
    log_message = f'Message deleted - {message.author} - {message.content}'
    logging.info(log_message)
    logging_channel = bot.get_channel(logging_channel_id)
    if logging_channel:
        embed = discord.Embed(title='Message Deleted', description=log_message, timestamp=datetime.datetime.now())
        embed.set_author(name=message.author, icon_url=message.author.avatar_url)
        await logging_channel.send(embed=embed)


# Run the bot
bot.run('YOUR_BOT_TOKEN')
