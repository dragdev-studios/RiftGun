import asyncio
import json
import os
import sys
import traceback
from typing import Optional, Union

import discord
import humanize
from discord.ext import commands

from .converters import GlobalTextChannel, GuildConverter


def print(*values: object, sep: Optional[str]=" ", end: Optional[str] = "\n", file=sys.stdout,
          flush: bool = False):
    """
    print(value, ..., sep=' ', end='\n', file=sys.stdout, flush=False)

    Prints the values to a stream, or to sys.stdout by default.
    Optional keyword arguments:
    file:  a file-like object (stream); defaults to the current sys.stdout.
    sep:   string inserted between values, default a space.
    end:   string appended after the last value, default a newline.
    flush: whether to forcibly flush the stream.
    """
    file.write("[RiftGun] " + sep.join(str(v) for v in values) + end)
    return ''

# def rift_admin(ctx: commands.Context):
#     if not ctx.guild:
#         raise commands.NoPrivateMessage()
#     else:
#         if not ctx.channel.permissions_for(ctx.author).manage_roles:
#             raise commands.MissingPermissions("manage_roles")
#         else:
#             return True
# May come back into use later?


class RiftGun(commands.Cog):
    """Need to see what others are doing and communicate with them? This two-way module is the thing for you!

    <https://github.com/dragdev-studios/RiftGun>"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        try:
            with open("./rifts.min.json") as rfile:
                data = json.load(rfile)
            print("Loaded data from existing data file.")
            self.data = data
        except (FileNotFoundError, json.JSONDecodeError):
            print("No existing file, or corrupted entries, defaulting to nothing. A new file will be created on cog"
                  " unload or command usage.", file=sys.stderr)
            self.data = {}

    def cog_unload(self):
        with open("./rifts.min.json", "w+") as wfile:
            json.dump(self.data, wfile)
        print("Saved data and unloaded module")

    def save(self):
        with open("./rifts.min.json", "w+") as wfile:
            json.dump(self.data, wfile)

    async def cog_check(self, ctx):
        if not await self.bot.is_owner(ctx.author): raise commands.NotOwner()
        else: return True

    def add_rift(self, source: discord.TextChannel, target: discord.TextChannel, notify: bool = True):
        self.data[str(target.id)] = {
            "source": source.id,
            "target": target.id,
            "notify": notify
        }
        self.save()
        if notify:
            self.bot.loop.create_task(target.send("\N{cinema} A rift has opened in this channel!"))
        return

    @commands.command(name="rifts", aliases=['openrifts'])
    async def open_rifts(self, ctx: commands.Context):
        """Shows all valid, open rifts."""
        y, n = "\N{white heavy check mark}", "\N{cross mark}"
        pag = commands.Paginator()
        for channel_id, _ in self.data.items():
            ic = int(channel_id)
            channel = self.bot.get_channel(ic)

            if not channel:
                pag.add_line(f"{n} {channel_id}")
                continue

            p: discord.Permissions = channel.permissions_for(channel.guild.me)
            if not all([p.read_messages, p.send_messages]):
                pag.add_line(f"{n} {channel.name} - {channel.guild.id}")
                continue
            else:
                pag.add_line(f"{y} {channel.name} - {channel.guild.id}")
        for page in pag.pages:
            await ctx.send(page)

    @commands.command(name="open", aliases=['openrift', 'or'])
    async def open_rift(self, ctx: commands.Context, notify: Optional[bool]=True, *, channel: GlobalTextChannel()):
        """Opens a rift into a channel.

        This will notify the channel that a rift has been opened.
        ---
        Notify - bool: Whether to send a notification to the channel the rift is opening in that it has opened
        Channel - GlobalChannel: What channel to open the rift in."""
        if channel == ctx.channel:
            return await ctx.send("\N{cross mark} You can't open a rift in this channel.")

        if self.data.get(str(channel.id)):
            return await ctx.send("\N{cross mark} You are already rifting to that channel!")

        channel: discord.TextChannel
        p = channel.permissions_for(channel.guild.me)
        if not all([p.read_messages, p.send_messages]):
            return await ctx.send("\N{cross mark} Insufficient permissions to access that channel.")

        self.add_rift(ctx.channel, channel, notify)
        return await ctx.send(f"\N{white heavy check mark} Opened a rift in #{channel.name}.")

    @commands.command(name="close", aliases=['closerift', 'cf'])
    async def close_rift(self, ctx: commands.Context, notify: Optional[bool]=True, *,
                         target: Union[GlobalTextChannel, int]):
        """Closes a rift.

        This command takes the same arguments as [p]openrift.
        If the bot can no longer see the rift channel, you can provide the ID instead and it will still be deleted"""
        if not isinstance(target, int):
            target: discord.TextChannel
            if notify and target.permissions_for(target.guild.me).send_messages:
                await target.send("\U00002601\U0000fe0f The rift collapsed!")

        if isinstance(target, int):
            if self.data.get(str(target)):
                del self.data[str(target)]
            else:
                return await ctx.send(f"\N{cross mark} That channel doesn't have an open rift.")
        else:
            if self.data.get(str(target.id)):
                del self.data[str(target.id)]
            else:
                return await ctx.send(f"\N{cross mark} That channel doesn't have an open rift.")
        self.save()
        return await ctx.send(f"\N{white heavy check mark} Closed the rift for {target}.")

    @commands.Cog.listener(name="on_message")
    async def message(self, message: discord.Message):
        context: commands.Context = await self.bot.get_context(message)
        if message.author == self.bot.user:
            return  # only ignore the current bot to prevent loops.
        elif context.valid:
            return

        sources = {}
        targets = {}
        sid = message.channel.id

        for target, source in self.data.items():
            sources[int(source["source"])] = int(target)
            targets[int(target)] = int(source["source"])

        if sid in sources.keys():
            channel = self.bot.get_channel(sources[sid])
            attachments = [a.to_file() for a in message.attachments]
            await channel.send(f"**{message.author}:** {message.clean_content}"[:2000],
                               embed=message.embeds[0] if message.embeds else None,
                               files=attachments or None)
        elif sid in targets.keys():
            channel = self.bot.get_channel(targets[sid])
            attachments = [a.to_file() for a in message.attachments]
            await channel.send(f"**{message.author}:** {message.clean_content}"[:2000],
                               embed=message.embeds[0] if message.embeds else None,
                               files=attachments or None)

    @commands.command(name="channelinfo", aliases=['ci', 'chaninfo', 'cinfo'])
    async def channel_info(self, ctx: commands.Context, *, channel: GlobalTextChannel()):
        """Shows you information on a channel before you open a rift in it

        This should be used to make sure you got the right channel before opening."""
        channel: discord.TextChannel
        nsfw = channel.is_nsfw()
        ago = channel.created_at.strftime("%c") + " " + humanize.naturaltime(channel.created_at)
        perms = channel.permissions_for(channel.guild.me).value
        e = discord.Embed(
            title=f"Name: {channel.name}",
            description="ID: `{0.id}`\nGuild: {0.guild.name} (`{0.guild.id}`)\nCategory: {0.category}\n"
                        "Slowmode: {0.slowmode_delay}\nNSFW: {1}\nCreated at: {2}\n"
                        "[Permissions Value]({3}): {4}".format(
                channel, nsfw, ago, f"https://discordapi.com/permissions.html#{perms}", str(perms)),
            color=channel.guild.owner.color,
            timestamp=channel.created_at
        )
        return await ctx.send(embed=e)

    @commands.command(name="channels")
    async def channels(self, ctx: commands.Context, *, guild: GuildConverter()):
        """Lists every channel that is in {guild}."""
        guild: discord.Guild
        types = {
            discord.CategoryChannel: ", ",
            discord.TextChannel: "#",
            discord.VoiceChannel: "\U0001f508"
        }
        p = commands.Paginator(max_size=2048)
        for category, channels in guild.by_category():
            if not category:
                for channel in channels:
                    prepre = ""
                    p.add_line(f"{prepre}{types[type(channel)]}{channel.name}")
            else:
                p.add_line(f", {category.name}")
                for channel in channels:
                    prepre = "| "
                    p.add_line(f"{prepre}{types[type(channel)]}{channel.name}")
            p.add_line(empty=True)

        for page in p.pages:
            await ctx.send(embed=discord.Embed(description=discord.utils.escape_mentions(
                page)))  # would use allowed_mentions, but since this is designed
            # to work with >=1.2.5, can't do that sadly.
            await asyncio.sleep(1)

    async def cog_command_error(self, ctx, error):
        if os.getenv("RG_EH"):
            try:
                rg = int(os.getenv("RG_EH"))
            except:
                print("Assuming you want logging since the env var \"RG_EH\" isn't an integer of 1 or 0.")
            else:
                if rg < 1: return
        error = getattr(error, "original", error)
        if isinstance(error, commands.BadArgument):
            return await ctx.send(f"Argument conversion error (an invalid argument was passed): `{error}`")
        elif isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(str(error))

        exc = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        print(f"Exception raised in command {ctx.command}: {str(error)}\n{exc}", file=sys.stderr)
        print("You can turn these warnings off by setting the environment variable \"RG_EH\" to 0")
        return await ctx.send(f"\N{cross mark} an error was raised, and printed to console. If the issue persists,"
                              f" please open an issue on github (<https://github.com/dragdev-studios/RiftGun/issues/new>)")
