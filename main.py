import asyncio
import logging
from datetime import datetime

import discord
from discord.ext import commands
from dotenv import load_dotenv

from lib.ZOutput import *
from lib.ZServer import *

# -- Bot init -------------------------------------------------------
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# -- Variables ------------------------------------------------------
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ANNOUNCEMENT_CHANNEL_ID = os.getenv("ANNOUNCEMENT_CHANNEL_ID")
SERVERS_CATEGORY_NAME = os.getenv("SERVERS_CATEGORY_NAME")
EUROBOROS_IP = os.getenv("EUROBOROS_IP")
SERVER_BRAND = os.getenv("SERVER_BRAND")
EUROBOROS_FIRST_PORT = 10666  # TSPG port starts at 10666 and seems to stop around 1720

abort = False

if BOT_TOKEN is None:
    print("Bot Token not found")
    abort = True
if ANNOUNCEMENT_CHANNEL_ID is None:
    print("Announcement Channel id not found")
    abort = True
if SERVERS_CATEGORY_NAME is None:
    print("Servers category name not found")
    abort = True
if EUROBOROS_IP is None:
    print("Euroboros IP not found")
    abort = True
if SERVER_BRAND is None:
    print("Server brand not found")
    abort = True

if abort:
    print("Aborting ...")
    quit()

assert BOT_TOKEN
assert ANNOUNCEMENT_CHANNEL_ID

ANNOUNCEMENT_CHANNEL_ID = int(ANNOUNCEMENT_CHANNEL_ID)

is_loop_active = False
loop_timer: int = 10 * 60  # 10 minutes
max_found_servers: int = 3
max_queries: int = 60

pinned_servers_port: set[int] = set()
last_post_had_players = True


# -- Commands -------------------------------------------------------

@bot.command()
@commands.has_role("Admin")
async def update(ctx):
    assert SERVERS_CATEGORY_NAME
    assert SERVER_BRAND
    assert EUROBOROS_IP
    assert SERVER_BRAND

    global last_post_had_players

    await ctx.send(f"Querying {max_queries} potential servers\nThis might take a while...")

    channels = await ctx.guild.fetch_channels()
    servers_category = ""

    # TODO: edit already existing channels is possible instead of removing them all

    for channel in channels:
        if channel.name == SERVERS_CATEGORY_NAME:
            servers_category = channel
            print("Servers category found")

        if SERVERS_CATEGORY_NAME in str(channel.category):
            if "✅" in channel.name or "❌" in channel.name:
                print(f'deleting {channel.name}')
                await channel.delete()

    # - Define which ports to query
    # TODO : remove duplicated ports already in the pinned servers
    await ctx.send(f"Pinned servers : {pinned_servers_port}")

    port_list: list[int] = list(pinned_servers_port)

    for port in range(EUROBOROS_FIRST_PORT, EUROBOROS_FIRST_PORT + max_queries):  # [10666, 10700]
        port_list.append(port)

    # - Query servers
    found_servers: list[ZServer] = []

    for port in port_list:
        if len(found_servers) >= max_found_servers:
            await ctx.send("Break !")
            break

        server = ZServer(EUROBOROS_IP, port, ZCommon.DEFAULT_FLAGS)

        try:
            server.QueryServer(timeout=1)
            server.ParseData()
        except TimeoutError:
            print("Server Timeout !")
            continue
        except Exception as e:
            print(e)
            continue

        server_name: str = server.serverDict["%serverName%"]

        if SERVER_BRAND in server_name:
            pinned_servers_port.add(port)
            found_servers.append(server)
        else:
            if port in pinned_servers_port:
                pinned_servers_port.remove(port)

    # - Sort by player count
    sort_function = lambda serv: serv.serverDict["%clientCount%"]
    found_servers.sort(key=sort_function, reverse=True)

    # - Get info from servers
    announcements_channel = ctx.guild.get_channel(ANNOUNCEMENT_CHANNEL_ID)
    post_in_announcement = False

    embed = discord.Embed(
        title=f"{len(found_servers)} servers found !",
        color=discord.Color.green(),
        timestamp=datetime.now()
    )

    for server in found_servers:
        player_count: int = server.serverDict["%clientCount%"]
        current_map: str = server.serverDict["%serverMap%"]
        server_name: str = server.serverDict["%serverName%"]
        server_name = server_name.replace(SERVER_BRAND, "")
        server_name = server_name[:-19]

        message = ""
        symbol = "✅" if player_count > 0 else "❌"

        channel_name = f'`{symbol}"᲼"{player_count}"᲼"play・{server_name}・{current_map}`'
        channel = await ctx.guild.create_text_channel(channel_name, category=servers_category)

        if player_count > 0:
            for player in server.players:
                name = player.playerDict["%playerName%"]
                ping = player.playerDict["%playerPing%"]
                score = player.playerDict["%playerScore%"]
                minutes = player.playerDict["%playerMinutes%"]
                spectator = "- SPECTATOR" if player.playerDict["%playerSpectate%"] == True else ""

                message += f" ╟═══  {name} - {score} pts - {minutes} min - {ping} ping {spectator}\n"

            post_in_announcement = True
            await channel.send(message)

        embed.add_field(name=f'{symbol}・ {player_count} player(s) ・ {server_name}・{current_map}\n',
                        value=message, inline=False)

    if post_in_announcement:
        message = await announcements_channel.send(embed=embed)
        await message.publish()
        last_post_had_players = True
    elif last_post_had_players:
        message = await announcements_channel.send(embed=embed)
        await message.publish()
        last_post_had_players = False

    await ctx.send(embed=embed)


@bot.command()
@commands.has_role("Admin")
async def start(ctx):
    global is_loop_active
    is_loop_active = True

    await ctx.send("Starting the loop.")

    while is_loop_active:
        await update(ctx)
        await ctx.send(f"Next loop in {loop_timer // 60} minute(s).")
        await asyncio.sleep(loop_timer)


@bot.command()
@commands.has_role("Admin")
async def stop(ctx):
    global is_loop_active
    is_loop_active = False

    await ctx.send("Stoping the loop.")


@bot.command()
@commands.has_role("Admin")
async def timer(ctx, minutes: int):
    # Discord only allows 10 messages to be published in an announcement channel per hour
    if 6 <= minutes <= 10:
        global loop_timer
        loop_timer = minutes * 60

        await ctx.send(f"Timer is now {minutes} minute(s).")
    else:
        await ctx.send(f"The timer must be between 6 and 10 minute(s).")


@bot.command()
@commands.has_role("Admin")
async def max_servers(ctx, value: int):
    if 1 <= value <= 6:
        global max_found_servers
        max_found_servers = value

        await ctx.send(f"max_found_servers is now {max_found_servers}.")
    else:
        await ctx.send(f"Between 1 and 6 servers max.")


@update.error
async def update_error(ctx, error):
    if isinstance(error, discord.DiscordServerError):
        await ctx.send(f"Discord server error in Update !\n=====\nError: {error}\n=====")
    else:
        await ctx.send(f"Error: {error}")


@start.error
async def start_error(ctx, error):
    if isinstance(error, discord.DiscordServerError):
        await ctx.send(f"Discord server error in Start !\n=====\nError: {error}\n=====")
    else:
        await ctx.send(f"Error: {error}")


@stop.error
async def stop_error(ctx, error):
    await ctx.send(f"Error: {error}")


@timer.error
async def timer_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await ctx.send(f"Usage : `!timer <minutes>`\nCurrent value : {loop_timer // 60} minutes")
    else:
        await ctx.send(f"Error: {error}")


@max_servers.error
async def max_servers_error(ctx, error):
    await ctx.send(f"Error: {error}")


@bot.command()
async def info(ctx):
    await ctx.send("```Code base by Caboose / SkipGrub\n"
                   "(https://zandronum.com/forum/viewtopic.php?t=9992)\n"
                   "(https://gitlab.com/SkipGrube/zquery)\n"
                   "\n"
                   "Discord Bot by Edewaa\n"
                   "\n"
                   "!update      -> update the server list\n"
                   "!start       -> start an update loop\n"
                   "!stop        -> stops the loop\n"
                   "!timer <min>     -> sets the timer duration in minutes\n"
                   "!max_servers <n> -> maximum number of servers\n```")


@bot.event
async def on_ready():
    print("Bot Logged in")


# -- Main -----------------------------------------------------------

bot.run(BOT_TOKEN, log_handler=handler, log_level=logging.DEBUG)
