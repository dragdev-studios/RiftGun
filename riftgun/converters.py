import discord
import typing
from discord.ext import commands


class GlobalTextChannel(commands.Converter):
    """A converter that attempts to find the closest match to the provided channel."""
    def __init__(self, *, sort_by_last_message: bool = True):
        self.sblm = sort_by_last_message

    async def convert(self, ctx, argument: str) -> discord.TextChannel:
        """Converts a provided argument to a text channel."""
        try:
            return await commands.TextChannelConverter().convert(ctx, argument)
        except commands.BadArgument:
            pass

        if argument.isdigit(): argument = int(argument)

        def match(channel: discord.TextChannel):
            if channel.id == argument:
                return True
            else:
                arg = str(argument)
                if channel.name.lower() == str(arg).lower():
                    return True
                elif channel.name in arg:
                    return True
                elif arg in channel.name:
                    return True

        channel = discord.utils.find(match, sorted(list(ctx.bot.get_all_channels()), key=lambda x: x.id))

        if channel: return channel
        else: raise commands.BadArgument(f"Unable to convert \"{argument}\" to TextChannel, globally or locally.")

    @staticmethod
    def convertSync(ctx, argument: str) -> discord.TextChannel:
        """Converts a provided argument to a text channel."""
        if argument.isdigit(): argument = int(argument)

        def match(channel: discord.TextChannel):
            if channel.id == argument:
                return True
            else:
                arg = str(argument)
                if channel.name.lower() == str(arg).lower():
                    return True
                elif channel.name in arg:
                    return True
                elif arg in channel.name:
                    return True

        channel = discord.utils.find(match, sorted(list(ctx.bot.get_all_channels()), key=lambda x: x.id))

        if channel: return channel
        else: raise commands.BadArgument(f"Unable to convert \"{argument}\" to TextChannel, globally or locally.")