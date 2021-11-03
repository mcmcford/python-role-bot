import time
import discord
import sqlite3
from random import random
from discord import Member
from discord.ext import commands
from discord_components import *
from discord.ext.commands import Bot
from discord.ext.commands import has_permissions, MissingPermissions
from discord_components import Button, Select, SelectOption, ComponentsBot

# variables
bot_token = ''
bots_prefix = "!"

# bot
bot = ComponentsBot(bots_prefix)

db = sqlite3.connect('config.db')
cursor = db.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS config(role_id TEXT, names TEXT, description TEXT, guild_id TEXT)')


# on ready print message to terminal
@bot.event
async def on_ready():
    print("Logged in as " + str(bot.user))
    print("User ID: " + str(bot.user.id))
    print("Time: " + str(time.time()))
    
    await bot.change_presence(activity=discord.Game(name="!rolehelp"))

# command to list all roles
@bot.command(pass_context=True)
@has_permissions(administrator=True)
async def listallroles(ctx):
    guild = ctx.message.guild
    roles = guild.roles

    message = ""

    for role in roles:
        if role.name != "@everyone":
            message += str(role.id) + " : " + role.name + "\n"
            if len(message) > 1900:
                await ctx.send(message)
                message = ""
    
    if message != "":
        await ctx.send(message)

# command to list roles in the config table
@bot.command(pass_context=True)
async def listroles(ctx):
    guild = ctx.message.guild

    cursor.execute('SELECT * FROM config WHERE guild_id = ?',(str(guild.id),))
    config = cursor.fetchall()

    message = ""

    for row in config:

        names = row[1].split(",")

        message += "<@&" + str(row[0]) + ">" + " : `!join " + names[0] + "`\n"

        if len(message) > 3800:
            style = discord.Embed(name="roles", title="Joinable Roles", description=message,  allowed_mentions = discord.AllowedMentions(users=False,roles=False), color=0x000000)
            await ctx.send(embed=style)
            message = ""
    
    if message != "":
        style = discord.Embed(name="roles", title="Joinable Roles", description=message,  allowed_mentions = discord.AllowedMentions(users=False,roles=False), color=0x000000)
        await ctx.send(embed=style)

# allow a person to join a role from the database
@bot.command(pass_context=True)
async def join(ctx, *, role_name):
    guild = ctx.message.guild
    member = ctx.message.author
    roles = guild.roles

    cursor.execute('SELECT * FROM config WHERE guild_id = ?',(str(guild.id),))
    config = cursor.fetchall()

    for row in config:
        names = row[1].split(",")
        if role_name.lower() in names:
            role = discord.utils.get(guild.roles, id=int(row[0]))

            if role in member.roles:
                await ctx.send("You already have this role!")
                return
            else:
                await member.add_roles(role)
                await ctx.send("You have joined the " + role.name + " role!")
                return
    
    await ctx.send("That role does not exist!")
    
# allow a person to leave a role from the database
@bot.command(pass_context=True)
async def leave(ctx, *, role_name):
    guild = ctx.message.guild
    member = ctx.message.author
    roles = guild.roles

    cursor.execute('SELECT * FROM config WHERE guild_id = ?',(str(guild.id),))
    config = cursor.fetchall()

    for row in config:
        names = row[1].split(",")
        if role_name.lower() in names:
            role = discord.utils.get(guild.roles, id=int(row[0]))

            if role in member.roles:
                await member.remove_roles(role)
                await ctx.send("You have left the " + role.name + " role!")
                return
            else:
                await ctx.send("You can't leave a role you don't have!")
                return
                
    await ctx.send("That role does not exist!")


bot.run(bot_token) 