from random import randint
from redbot.core import commands


class OneTrueGod:
    """Everything was Nicolas Cage."""

    __author__ = 'UltimatePancake'
    __version__ = '0.2'

    @commands.command(aliases=['cage'])
    async def onetruegod(self, ctx):
        """Post random Nicolas Cage image from placecage.com"""

        placecage = 'https://www.placecage.com'
        width = randint(200, 700)
        height = randint(200, 700)
        await ctx.send(f'{placecage}/{width}/{height}')
