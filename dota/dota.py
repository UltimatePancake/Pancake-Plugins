import asyncio
import aiohttp
import discord
from bs4 import BeautifulSoup
from discord.ext import commands
from random import randint
from redbot.core import Config
from redbot.core.utils.chat_formatting import error, info, box
from tabulate import tabulate


class Dota:
    """User info"""

    __author__ = "UltimatePancake"
    __version__ = "0.2"

    def __init__(self, *args, **kwargs):
        self.config = Config.get_conf(self, identifier=4831679513)
        default_user = {
            "dotabuff_id": ""
        }
        self.config.register_user(**default_user)
        self.dotabuff_url = 'https://www.dotabuff.com/players'
        self.req_header = {'User-Agent': 'Friendly redbot'}

    async def _idcheck(self, ctx):
        id_val = await self.config.user(ctx.message.author).dotabuff_id()
        if id_val:
            return True
        msg = await ctx.send(error('You have not set a dotabuff id yet.'))
        await asyncio.sleep(20)
        await msg.delete()
        return False

    @commands.group(autohelp=True)
    async def dota(self, ctx):
        """Dota player info ~~stolen~~ retrieved from dotabuff.com"""
        pass

    @dota.command()
    async def idset(self, ctx, dotabuff_id: str):
        """Sets dotabuff id for user"""
        await self.config.user(ctx.message.author).dotabuff_id.set(dotabuff_id)
        if await self._idcheck(ctx.message.author):
            msg = await ctx.send(info(f'{ctx.message.author.name} id set to {dotabuff_id}.'))
        else:
            msg = await ctx.send(error('You have not set a dotabuff id yet.'))
        await asyncio.sleep(20)
        await msg.delete()

    @dota.command()
    async def profile(self, ctx):
        """Gets general player info"""
        if not await self._idcheck(ctx):
            return

        dotabuff_id = await self.config.user(ctx.message.author).dotabuff_id()
        url = f'{self.dotabuff_url}/{dotabuff_id}'

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.req_header) as r:
                soup = BeautifulSoup(await r.text(), 'html.parser')

        img = soup.find('img', {'class': 'image-player image-bigavatar'})
        rank = soup.find('div', {'class': 'rank-tier-wrapper'})['title']
        rank_img = soup.find('img', {'class': 'rank-tier-base'})['src']
        wins = int(soup.find('span', {'class': 'wins'}).string)
        losses = int(soup.find('span', {'class': 'losses'}).string)
        abandons = int(soup.find('span', {'class': 'abandons'}).string)

        last_match = soup.find('div', {'class': 'header-content-secondary'}).find('time').string
        heroes_overview = soup.find('div', {'class': 'heroes-overview'})
        hero_rows = heroes_overview.findAll('div', {'class': 'r-row'})
        heroes = {
            'Name': [],
            'Matches': [],
            'Win %': [],
            'KDA': []
        }

        for hero in hero_rows:
            hero_data = hero.findAll(text=True)
            heroes['Name'].append(hero_data[1])
            heroes['Matches'].append(hero_data[4])
            heroes['Win %'].append(hero_data[6])
            heroes['KDA'].append(hero_data[8])

        hero_table = tabulate(heroes, headers="keys")

        win_rate = (wins / (wins + losses + abandons)) * 100
        win_rate_pct = f'{round(win_rate, 2):.2f}%'

        em = discord.Embed(colour=randint(0, 0xFFFFFF))
        em.set_author(name=f'{img["title"]} - {rank}')
        em.set_thumbnail(url=rank_img)
        em.add_field(name='Record', value=f'{wins} - {losses} - {abandons}')
        em.add_field(name='Win Rate', value=win_rate_pct)
        em.add_field(name='Top heroes', value=box(hero_table))
        em.set_footer(text=f'Last match: {last_match}', icon_url=img['src'])
        em.url = url

        await ctx.send(embed=em)

    @dota.command()
    async def records(self, ctx):
        """Gets player records"""
        if not await self._idcheck(ctx):
            return

        dotabuff_id = await self.config.user(ctx.message.author).dotabuff_id()
        url = f'{self.dotabuff_url}/{dotabuff_id}/records'

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.req_header) as r:
                soup = BeautifulSoup(await r.text(), 'html.parser')

        img = soup.find('img', {'class': 'image-player image-bigavatar'})
        cards = soup.findAll('div', {'class': 'card'})
        records = {}

        for card in cards:
            k = card.find('div', {'class': 'title'}).contents[0]
            v = card.find('div', {'class': 'value'}).contents[0]
            h = card.find('div', {'class': 'hero'}).contents[0]
            records[k] = {'value': v, 'hero': h}

        em = discord.Embed(colour=randint(0, 0xFFFFFF))
        em.set_author(name=f'{img["title"]} - Records')
        em.set_thumbnail(url=img['src'])
        
        for k, v in records.items():
            hero = v['hero'].split('  ')
            em.add_field(name=k, value=f'{v["value"]} ({hero[0]})')

        em.url = url

        await ctx.send(embed=em)
