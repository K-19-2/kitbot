# bot.py
import os
import random
import discord
import asyncio

from discord.ext import commands
from discord.ext import tasks
from dotenv import load_dotenv
from datetime import datetime


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Change only the no_category default string

help_command = commands.DefaultHelpCommand(no_category = 'Commands')

bot = commands.Bot(case_insensitive=True, command_prefix='$', description="The Kitchen Quote Bot and daily topic changer! Created by K-19#0658.",
help_command=help_command)

topicLine = 0

#as soon as the bot starts, launches these

@bot.event 
async def on_ready():

    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="The Kitchen Discord"))
    print("Bot Ready, sending ready message and beginning loop.")
    
    timer = 1
    while timer > 0: #loops the 'timer' to call the change
        await checkTime()
        await asyncio.sleep(1)

#time checking and calling the change
async def checkTime():

    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    #print("Current Time =", current_time) #prints current time

    if(current_time == '09:00:00'):
        await topicChange()
        
#topic changing
async def topicChange():
    global topicLine
    channel = bot.get_channel(815280183325098004) #set channel id here
    with open("topics.txt", "r") as fin:
        try:
            lines = fin.readlines()
            topicLine += 1
            await channel.edit(name="\N{CALENDAR}daily-topic-" + lines[topicLine])
            print('Next Change,', lines[topicLine])
        except IndexError:
            print("Restarting Topic Count.")
            topicLine = 0
            await channel.edit(name="\N{CALENDAR}daily-topic-" + lines[topicLine])

#list available topics and their respective numbers
@bot.command(name="listtopics", help="- Lists all of the available topics.")
async def listtopics(ctx):
    if ctx.message.author.guild_permissions.administrator or ctx.message.author.guild_permissions.manage_channels or ctx.message.author.guild_permissions.manage_roles:
        tlnum = -1
        with open("topics.txt", "r") as fl:
            tllines = fl.readline()
            fl.seek(0)
            for tllines in fl:
                await ctx.send("{} - {}".format(tlnum, tllines))
                tlnum += 1
    else:
        await ctx.send("This command is only available to administrators.")

#topic add command/error handling.
@bot.command(name="addtopic", help="- For administrators to add a topic. Note: if it is a multi-word topic, enclose the topic in quotes, such as \"Toxic MugenZ\".")
async def addtopic(ctx, topics):
    if ctx.message.author.guild_permissions.administrator or ctx.message.author.guild_permissions.manage_channels or ctx.message.author.guild_permissions.manage_roles:
        with open("topics.txt", "a") as f:
            f.write(topics + "\n")
        await ctx.send("Added \'" + topics + "\' to the topics file.")
    else:
        await ctx.send("Please have an Admin add your topic to the list, if approved.")

@addtopic.error
async def addtopicerror(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send("Please type a topic. For example, $addtopic plsno or $addtopic \"pls no\".")

#topic skip
@bot.command(name="skiptopic", help="- For administrators to skip the topic, if so preferred.")
async def skiptopic(ctx):
    if ctx.message.author.guild_permissions.administrator or ctx.message.author.guild_permissions.manage_channels or ctx.message.author.guild_permissions.manage_roles:
        await ctx.send("Topic changed. Note: Discord limits channel name changes to about 2 per 10 minutes.")
        await topicChange()
    else:
        await ctx.send("Please contact an administrator to change the topic.")

#manual topic change/error handling
@bot.command(name="topic", help="- For administrators to manually change the topic.")
async def mantopic(ctx, topicnum):
    global topicLine
    if ctx.message.author.guild_permissions.administrator or ctx.message.author.guild_permissions.manage_channels or ctx.message.author.guild_permissions.manage_roles:
        with open("topics.txt", "r") as mantopicf:
            try:
                global topicLine
                mantopicfl = mantopicf.readlines()
                topicLine = int(topicnum)
                await ctx.send("Topic manually changed to topic: " + mantopicfl[topicLine + 1] + "If no topic was found with that number, the first topic will be used. Note: Discord limits channel name changes to about 2 per 10 minutes.")
                await topicChange()
            except ValueError:
                await ctx.send("Please type a topic number.")
            except IndexError:
                await ctx.send("Please type a valid topic number.")

    else:
        await ctx.send("Please contact an administrator to change the topic.")

@mantopic.error
async def mantopicerror(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send("Please specify a topic number.")


#emergency shutdown function
@bot.command(name="shutdown", help="- Emergency shutdown for administrators.")
async def shutdown(ctx):
    if ctx.message.author.guild_permissions.administrator or ctx.message.author.guild_permissions.manage_channels or ctx.message.author.guild_permissions.manage_roles: #check admin, hopefully works
        await ctx.send("Shutting down bot.")
        exit()
    else:
        await ctx.send("I\'m sorry, Dave. I can\'t let you do that.")
        return

#basic quote functions
@bot.command(name='q',aliases=['quote', 'quotes'], help='- Responds with a random quote from \'The Kitchen\' quotes. \'quote\' and \'quotes\' can aslo be used.')
async def kitchenQ(ctx):

    imgList = os.listdir("./All_Images")
    imgString = random.choice(imgList)
    path = "./All_Images/" + imgString

    file = discord.File(path)
    await ctx.send(file = file)



bot.run(TOKEN)
