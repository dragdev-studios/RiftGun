import json
from typing import Optional

import discord
import sys
import io

from discord.ext import commands
from .converters import GlobalTextChannel


def print(*values: object, sep: Optional[str]=" ", end: Optional[str] = "\n", file: Optional[io.StringIO]=sys.stdout,
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

def rift_admin(ctx: commands.Context):
    if not ctx.guild:
        raise commands.NoPrivateMessage()
    else:
        if not ctx.channel.permissions_for(ctx.author).manage_roles:
            raise commands.MissingPermissions("manage_roles")
        else:
            return True


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
            print("No existing file, or corrupted entries, defaulting to nothing.")
            self.data = {}

    def cog_unload(self):
        with open("./rifts.min.json", "w+") as wfile:
            json.dump(self.data, wfile)
        print("Saved data and unloaded module")

    def save(self):
        with open("./rifts.min.json", "w+") as wfile:
            json.dump(self.data, wfile)

    async def cog_check(self, ctx):
        if not self.bot.is_owner(ctx.author): raise commands.NotOwner()
        else: return True

    def add_rift(self, source: discord.TextChannel, target: discord.TextChannel, notify: bool = True):
        self.data[str(target.id)] = {
            "source": source.id,
            "target": target.id,
            "notify": notify
        }
        self.save()
        if notify:
            await target.send("\N{cinema} A rift has opened in this channel!")
        return

    @commands.command(name="rifts", aliases=['r', 'openrifts'])
    async def open_rifts(self, ctx: commands.Context):
        """Shows all valid, open rifts."""
        y, n = "\N{white heavy check mark}", "\N{cross mark}"
        pag = commands.Paginator()
        for channel_id, webhook_url in self.data.items():
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

        channel: discord.TextChannel
        p = channel.permissions_for(channel.guild.me)
        if not all([p.read_messages, p.send_messages]):
            return await ctx.send("\N{cross mark} Insufficient permissions to access that channel.")

        self.add_rift(ctx.channel, channel, notify)
        return await ctx.send(f"\N{white heavy check mark} Opened a rift in #{channel.name}.")

    @commands.Cog.listener(name="on_message")
    async def message(self, message: discord.Message):
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
                               embeds=message.embeds or None,
                               files=attachments or None)
        elif sid in targets.keys():
            channel = self.bot.get_channel(targets[sid])
            attachments = [a.to_file() for a in message.attachments]
            await channel.send(f"**{message.author}:** {message.clean_content}"[:2000],
                               embeds=message.embeds or None,
                               files=attachments or None)