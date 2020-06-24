import discord
from discord.ext import commands


class GlobalConverter(commands.Converter):
    """The ABC class for global converters"""

    async def convert(self, ctx: commands.Context, argument: str):
        raise NotImplementedError

    @staticmethod
    def convertSync(ctx: commands.Context, argument: str):
        raise NotImplementedError


class GlobalTextChannel(GlobalConverter):
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

        if channel:
            return channel
        else:
            raise commands.BadArgument(f"Unable to convert \"{argument}\" to TextChannel, globally or locally.")

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

        if channel:
            return channel
        else:
            raise commands.BadArgument(f"Unable to convert \"{argument}\" to TextChannel, globally or locally.")


class GuildConverter(GlobalConverter):
    """Converts a provided guild name/id into a discord.Guild"""

    @staticmethod
    def convertSync(ctx: commands.Context, argument: str):
        for guild in ctx.bot.guilds:
            if str(guild.id) == argument:
                return guild
            elif guild.name.lower() == argument.lower():
                return guild
            elif guild.name.lower() in argument.lower():
                return guild
            elif argument.lower() in guild.name.lower():
                return guild
            else:
                continue
        raise commands.BadArgument(f"Unable to convert \"{argument}\" to guild.")

    async def convert(self, ctx: commands.Context, argument: str):
        return self.convertSync(ctx, argument)
