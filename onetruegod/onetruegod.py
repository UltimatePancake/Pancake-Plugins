from random import randint
from discord.ext import commands


class OneTrueGod:
    """Everything was Nicolas Cage."""

    @commands.command(aliases=['onetruegod', 'cage'])
    async def _cage(self, ctx):
        """Post random Nicolas Cage image from placecage.com"""

        placecage = 'https://www.placecage.com'
        width = randint(200, 700)
        height = randint(200, 700)
        await ctx.send('{}/{}/{}'.format(placecage, width, height))
