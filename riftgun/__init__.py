from .cog import RiftGun


def setup(bot):
    bot.add_cog(RiftGun(bot))