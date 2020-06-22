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

        for target, source in self.data.items():
            sources[int(source["source"])] = int(target)
            targets[int(target)] = int(source["source"])

        if sid in targets.keys():
            channel = self.bot.get_channel(targets[sid])
            attachments = [a.to_file() for a in message.attachments]
            await channel.send(f"**{message.author}:** {message.clean_content}"[:2000],
                               embed=message.embeds[0] if message.embeds else None,
                               files=attachments or None)


def setup(bot: commands.Bot):
    if bot.get_cog("RiftGun"):
        bot.unload_extension("riftgun")
    bot.add_cog(OneWayRiftGun(bot))
