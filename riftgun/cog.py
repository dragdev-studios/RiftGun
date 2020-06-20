import json
from typing import Optional

import discord
import sys
import io

from discord.ext import commands


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

    async def cog_check(self, ctx):
        if not self.bot.is_owner(ctx.author): raise commands.NotOwner()
        else: return True

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
