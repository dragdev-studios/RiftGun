import discord
from discord.ext import commands

from .cog import RiftGun


class OneWayRiftGun(RiftGun):
    """The rift gun, but one-way instead."""

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
        embeds = [embed for embed in message.embeds if embed.type == "rich"] or None

        for target, source in self.data.items():
            sources[int(source["source"])] = int(target)
            targets[int(target)] = int(source["source"])

        if sid in targets.keys():
            channel = self.bot.get_channel(targets[sid])
            self.queue.put_nowait(channel.send(f"**{message.author}:** {message.clean_content}"[:2000],
                                               embed=embeds))
            if message.attachments:
                self.queue.put_nowait(f"*Attachments:*\n{' '.join(x.url for x in message.attachments)}")


def setup(bot: commands.Bot):
    if bot.get_cog("RiftGun"):
        bot.unload_extension("riftgun")
    bot.add_cog(OneWayRiftGun(bot))
