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

        def match(channel: typing.Union[discord.TextChannel, discord.VoiceChannel, discord.CategoryChannel]):
            if channel.id == argument:
                return True
            else:
                if channel.name.lower() == argument.lower():
                    return True
                elif channel.name in argument:
                    return True
                elif argument in channel.name:
                    return True

        channel = discord.utils.find(match, sorted(ctx.bot.channels, key=lambda x: x.last_message))

        if channel: return channel
        else: raise commands.BadArgument(f"Unable to convert \"{argument}\" to TextChannel, globally or locally.")

    @staticmethod
    def convertSync(ctx, argument: str) -> discord.TextChannel:
        """Converts a provided argument to a text channel."""
        if argument.isdigit(): argument = int(argument)

        def match(channel: typing.Union[discord.TextChannel, discord.VoiceChannel, discord.CategoryChannel]):
            if channel.id == argument:
                return True
            else:
                if channel.name.lower() == argument.lower():
                    return True
                elif channel.name in argument:
                    return True
                elif argument in channel.name:
                    return True

        channel = discord.utils.find(match, sorted(ctx.bot.channels, key=lambda x: x.last_message))

        if channel: return channel
        else: raise commands.BadArgument(f"Unable to convert \"{argument}\" to TextChannel, globally or locally.")

    def __call__(self, *args, **kwargs):
        self.convertSync(args[0], args[1])