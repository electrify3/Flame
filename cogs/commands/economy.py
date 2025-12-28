import aiosqlite
import datetime
import random
import typing

from dataclasses import dataclass
from typing import List, Sequence, Tuple

import discord
from discord import app_commands
from discord.ext import commands

from utils.paginator import Paginator

if typing.TYPE_CHECKING:
    from main import Bot


class DataBaseClient:
    def __init__(self, path: str, *, enable_foreignkey: bool = False, enable_wal: bool = True) -> None:
        self.path = path
        self.enable_foreignkey: bool = enable_foreignkey
        self.enable_wal: bool = enable_wal
        self.connection: aiosqlite.Connection | None = None
    
    async def setup_connection(self) -> aiosqlite.Connection:
        if not self.connection:

            self.connection = await aiosqlite.connect(self.path)
            self.connection.row_factory = aiosqlite.Row

            if self.enable_foreignkey:
                await self.connection.execute("PRAGMA foreign_keys = ON")
            if self.enable_wal:
                await self.connection.execute("PRAGMA journal_mode = WAL")
        
        return self.connection
    
    async def close_connection(self) -> None:
        if self.connection:
            await self.connection.close()
            self.connection = None


@dataclass(slots=True)
class EconomyMember:
    guild_id: int
    user_id: int
    money: int
    bank: int
    last_claim: int



class EconomyClient(DataBaseClient):
    def __init__(self) -> None:
        super().__init__(
            'data/database/economy.db',
            enable_foreignkey=True)
        
    
    async def setup_table(self) -> None:
        await self.setup_connection()
        await self.connection.execute(f"""CREATE TABLE IF NOT EXISTS economy(
            guild_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            money INTEGER NOT NULL DEFAULT 0,
            bank INTEGER NOT NULL DEFAULT 0,
            last_claim INTEGER NOT NULL DEFAULT 0,
            
            PRIMARY KEY (guild_id, user_id))""")
        await self.connection.commit()

    async def add_member(self, member: discord.Member, *, money: int = 0) -> EconomyMember:
        await self.setup_connection()
        await self.connection.execute("""INSERT INTO economy(guild_id, user_id, money) VALUES(?, ?, ?)
            ON CONFLICT (guild_id, user_id) DO NOTHING""", (member.guild.id, member.id, money))

        await self.connection.commit()
        return EconomyMember(guild_id=member.guild.id, user_id=member.id, money=money, bank=0, last_claim=0)


    async def get_members(self, guild: discord.Guild) -> List[EconomyMember]:
        await self.setup_connection()
        async with self.connection.execute("""SELECT guild_id, user_id, money, bank, last_claim FROM economy WHERE guild_id = ? ORDER BY (money + bank) DESC""", (guild.id,)) as cur:
            rows = await cur.fetchall()
            return [EconomyMember(**row) for row in rows]
    

    async def get_member(self, member: discord.Member, *, create: bool = True) -> EconomyMember | None:
        await self.setup_connection()
        async with self.connection.execute("SELECT guild_id, user_id, money, bank, last_claim FROM economy WHERE guild_id = ? AND user_id = ?", (member.guild.id, member.id)) as cur:
            row = await cur.fetchone()

            if not row and create:
                return await self.add_member(member)
            
            return EconomyMember(**row) if row else None
    
    
    async def add_balance(self, member: discord.Member, money: int) -> None:
        await self.setup_connection()

        await self.connection.execute("""
            INSERT INTO economy (guild_id, user_id, money)
            VALUES (?, ?, ?)
            ON CONFLICT(guild_id, user_id)
            DO UPDATE SET money = money + excluded.money""", (member.guild.id, member.id, money))

        await self.connection.commit()
    
    async def deduct_balance(self, member: discord.Member, money: int) -> None:
        await self.setup_connection()

        await self.connection.execute("""
            INSERT INTO economy (guild_id, user_id, money)
            VALUES (?, ?, ?)
            ON CONFLICT(guild_id, user_id)
            DO UPDATE SET money = money - excluded.money""", (member.guild.id, member.id, money))

        await self.connection.commit()
    

    async def add_bank(self, member: discord.Member, money: int) -> None:
        await self.setup_connection()

        await self.connection.execute("""
            INSERT INTO economy (guild_id, user_id, bank)
            VALUES (?, ?, ?)
            ON CONFLICT(guild_id, user_id)
            DO UPDATE SET bank = bank + excluded.bank""", (member.guild.id, member.id, money))

        await self.connection.commit()
    

    async def deduct_bank(self, member: discord.Member, money: int) -> None:
        await self.setup_connection()

        await self.connection.execute("""
            INSERT INTO economy (guild_id, user_id, bank)
            VALUES (?, ?, ?)
            ON CONFLICT(guild_id, user_id)
            DO UPDATE SET bank = bank - excluded.bank""", (member.guild.id, member.id, money))

        await self.connection.commit()



    async def update_balance(self, member: discord.Member, money: int) -> None:
        await self.setup_connection()

        await self.connection.execute("""INSERT INTO economy (guild_id, user_id, money)
            VALUES (?, ?, ?)
            ON CONFLICT(guild_id, user_id)
            DO UPDATE SET money = excluded.money""", (member.guild.id, member.id, money))
        await self.connection.commit()
    

    async def update_bank(self, member: discord.Member, money: int) -> None:
        await self.setup_connection()

        await self.connection.execute("""INSERT INTO economy (guild_id, user_id, bank)
            VALUES (?, ?, ?)
            ON CONFLICT(guild_id, user_id)
            DO UPDATE SET bank = excluded.bank""", (member.guild.id, member.id, money))
        await self.connection.commit()
    

    async def update_claim(self, member: discord.Member) -> None:
        await self.setup_connection()

        await self.connection.execute("""INSERT INTO economy (guild_id, user_id, last_claim)
            VALUES (?, ?, ?)
            ON CONFLICT(guild_id, user_id)
            DO UPDATE SET last_claim = excluded.last_claim""", (member.guild.id, member.id, int(datetime.datetime.now(datetime.UTC).timestamp())))
        await self.connection.commit()


    async def get_rank(self, member: discord.Member) -> int:
        await self.setup_connection()

        async with self.connection.execute("""SELECT (money + bank) AS net FROM economy WHERE guild_id = ? AND user_id = ?""", (member.guild.id, member.id)) as cur:
            row = await cur.fetchone()
        
        if not row:
            await self.add_member(member)
            return await self.get_rank(member)
        
        net = row['net']

        async with self.connection.execute("""SELECT COUNT(*) AS better FROM economy WHERE guild_id = ? AND (money + bank) > ?""", (member.guild.id, net)) as cur:
            rank_row = await cur.fetchone()

        return rank_row["better"] + 1
        



class ShopClient(DataBaseClient):
    def __init__(self) -> None:
        super().__init__(
            'data/database/economy.db',
            enable_foreignkey=True)
        
    
    async def setup_table(self) -> None:
        await self.setup_connection()
            
        await self.connection.execute("""CREATE TABLE IF NOT EXISTS shop_items(
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER NOT NULL,
            
            item_name TEXT NOT NULL,
            description TEXT,

            buy_price INTEGER NOT NULL,
            sell_price INTEGER,
            use_price INTEGER DEFAULT 0,

            stock INTEGER DEFAULT -1,
            instant_use INTEGER DEFAULT 0,

            role_taken INTEGER,
            role_given INTEGER,
            role_required INTEGER,
            
            UNIQUE (guild_id, item_id))""")
        await self.connection.execute("CREATE INDEX IF NOT EXISTS idx_shop_items_guild ON shop_items(guild_id)")
        await self.connection.commit()


class InventoryClient(DataBaseClient):
    def __init__(self) -> None:
        super().__init__(
            'data/database/economy.db',
            enable_foreignkey=True)
        
    
    async def setup_table(self) -> None:
        await self.setup_connection()

        await self.connection.execute("""CREATE TABLE IF NOT EXISTS inventories(
            guild_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            CHECK (quantity > 0),
            PRIMARY KEY (guild_id, user_id, item_id),
            FOREIGN KEY (guild_id, item_id)
                REFERENCES shop_items(guild_id, item_id))""")
        await self.connection.execute("CREATE INDEX IF NOT EXISTS idx_inventories_user ON inventories(guild_id, user_id)")
        await self.connection.commit()




class Controller(Paginator):
    def __init__(self, ctx, items, page, max_pages):
        super().__init__(ctx, items, page, max_pages)

    def make_page(self) -> discord.Embed:
        description = "\n".join(data for data in self.items[self.page*10-10:self.page*10])
        embed = discord.Embed(title="Economy Leaderboard", description=description[:4000], color=self.ctx.bot.color)
        embed.set_author(name=self.ctx.me, icon_url=self.ctx.me.display_avatar.url)
        embed.set_footer(text=f"Page {self.page}/{self.max_pages}\t | \tUse {self.ctx.prefix}balance to view your balance.")
        return embed





class Economy(commands.Cog):
    def __init__(self, bot: 'Bot'):
        self.bot: Bot = bot

        self.economy: EconomyClient = EconomyClient()
        self.shop: ShopClient = ShopClient()
        self.inventory: InventoryClient = InventoryClient()

        self.currency: str = '<a:Ecash:1107707464650076322>'
        self.emoji = "<:Eeconomy:1444691668505985096>"

        with open('data/dialogues/works.txt') as works, open('data/dialogues/successful_crimes.txt') as s_crimes, open('data/dialogues/failed_crimes.txt') as f_crimes:
            self.works: list[str] = works.readlines()
            self.successful_crimes: list[str] = s_crimes.readlines()
            self.failed_crimes: list[str] = f_crimes.readlines()
    

    def format_money(self, money: int) -> str:
        if money < 0:
            return f'- {self.currency} {abs(money):,}'
        return f'{self.currency} {money:,}'


    def format_rank(self, rank: int) -> str:
        if 10 <= rank % 100 <= 20:
            suffix = "th"
        else:
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(rank % 10, "th")
        return f"{rank}{suffix}"
    

    def percentage(self, amount: int | float, percent: int | float, *, return_int: bool = True) -> int | float:
        value =  (percent / 100) * amount
        return int(value) if return_int else value


    def make_embed(self, user: discord.User, money: int, text: str) -> discord.Embed:
        embed = discord.Embed(timestamp=datetime.datetime.now(datetime.UTC))
        embed.set_author(name=user.name, icon_url=user.avatar.url if user.avatar else user.default_avatar.url)
        embed.set_footer(text=f'ID: {user.id}')

        if money > 0:
            embed.color = discord.Colour.green()
            embed.description = text.replace('$money', self.format_money(money))
        else:
            embed.color = discord.Colour.red()
            embed.description = text.replace('$money', self.format_money(money))

        return embed


    @commands.Cog.listener("on_ready")
    async def setup(self) -> None:
        await self.economy.setup_table()
        await self.shop.setup_table()
        await self.inventory.setup_table()


    @commands.hybrid_command(name='work',description='Makes some small money.', aliases=['earn'], usage='work')
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def work(self, ctx: commands.Context) -> None:
        money: int = random.randint(1, 5000)
        dialouge: str = random.choice(self.works)

        await self.economy.add_balance(ctx.author, money)
        embed: discord.Embed = self.make_embed(ctx.author, money, dialouge)
        await ctx.send(embed=embed)


    @commands.hybrid_command(name='crime',description='Commits a crime, it can make you more money with a risk of fine.', usage='crime')
    @commands.guild_only()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def crime(self, ctx: commands.Context) -> None:
        money: int = random.randint(1, 10000) * random.choice([-1, 1])
        dialouge: str = random.choice(self.successful_crimes if money > 0 else self.failed_crimes)

        await self.economy.add_balance(ctx.author, money)

        embed: discord.Embed = self.make_embed(ctx.author, money, dialouge)
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='balance', description='Shows cureent balance of the member.', aliases=['bal', 'cash', 'money'], usage='balance [member]')
    @commands.guild_only()
    async def balance(self, ctx: commands.Context, member: discord.Member = commands.Author) -> None:
        
        data = await self.economy.get_member(member)
        rank = await self.economy.get_rank(member)

        embed = discord.Embed(description=f"Leaderboard Rank: {self.format_rank(rank)}", timestamp=datetime.datetime.now(datetime.UTC), colour=discord.Colour.blue())
        embed.set_author(name=member.name, icon_url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.set_footer(text=f'ID: {member.id}')

        embed.add_field(name="Cash", value=self.format_money(data.money))
        embed.add_field(name="Bank", value=self.format_money(data.bank))
        embed.add_field(name="Total", value=self.format_money(data.money + data.bank))
        await ctx.send(embed=embed)
    


    @commands.hybrid_command(name='deposite', description='Deposites current money into your bank.', aliases=['dep'], usage='deposite [amount | all]')
    @commands.guild_only()
    async def deposite(self, ctx: commands.Context, amount: str) -> None:
        if amount.isdigit(): amount = int(amount)

        if isinstance(amount, str):
            if amount.lower() != 'all':
                embed = self.make_embed(ctx.author, -1, f"{self.bot.warning} | Invalid amount {amount}!")
                await ctx.send(embed=embed)
            else:
                member = await self.economy.get_member(ctx.author)
                if member.money <= 0:
                    await ctx.send(f"{self.bot.warning} | You can't deposite {self.format_money(member.money)} in your bank!")
                else:
                    await self.economy.add_bank(ctx.author, member.money)
                    await self.economy.deduct_balance(ctx.author, member.money)
                    embed = self.make_embed(ctx.author, member.money, f"{self.bot.success} | Deposited $money to your bank!")
                    await ctx.send(embed=embed)
        else:
            member = await self.economy.get_member(ctx.author)
            if member.money <= 0:
                await ctx.send(f"{self.bot.warning} | You can't deposite {self.format_money(member.money)} in your bank!")
            elif member.money < amount:
                await ctx.send(f"{self.bot.warning} | You don't have {self.format_money(amount)} in hands!")
            else:
                await self.economy.add_bank(ctx.author, amount)
                await self.economy.deduct_balance(ctx.author, amount)
                embed = self.make_embed(ctx.author, amount, f"{self.bot.success} | Deposited $money to your bank!")
                await ctx.send(embed=embed)

        


    @commands.hybrid_command(name='withdraw', description='Withdraws money from your bank.', aliases=['with'], usage='withdraw [amount | all]')
    @commands.guild_only()
    async def withdraw(self, ctx: commands.Context, amount: str) -> None:
        if amount.isdigit(): amount = int(amount)

        if isinstance(amount, str):
            if amount.lower() != 'all':
                embed = self.make_embed(ctx.author, -1, f"{self.bot.warning} | Invalid amount {amount}!")
                await ctx.send(embed=embed)
            else:
                member = await self.economy.get_member(ctx.author)
                if member.bank <= 0:
                    await ctx.send(f"{self.bot.warning} | You don't have enough money in your bank!")
                else:
                    await self.economy.deduct_bank(ctx.author, member.bank)
                    await self.economy.add_balance(ctx.author, member.bank)
                    embed = self.make_embed(ctx.author, member.bank, f"{self.bot.success} | Withdrew $money from your bank!")
                    await ctx.send(embed=embed)
        else:
            member = await self.economy.get_member(ctx.author)
            if member.bank <= 0 or member.bank < amount:
                await ctx.send(f"{self.bot.warning} | You don't have enough money in your bank!")
            else:
                await self.economy.deduct_bank(ctx.author, amount)
                await self.economy.add_balance(ctx.author, amount)
                embed = self.make_embed(ctx.author, amount, f"{self.bot.success} | Withdrew $money from your bank!")
                await ctx.send(embed=embed)


    @commands.hybrid_command(name='give', description='Use this command to pay money to other member.', aliases=['pay', 'send'], usage='give <member> <amount>')
    @commands.guild_only()
    @app_commands.describe(member='Member whom you want to pay money.', amount='Amount of money you want to pay.')
    async def give(self, ctx: commands.Context, member: discord.Member, amount: str) -> None:
        if amount.isdigit(): amount = int(amount)

        if isinstance(amount, str):
            if amount.lower() != 'all':
                embed = self.make_embed(ctx.author, -1, f"{self.bot.warning} | Invalid amount {amount}!")
                await ctx.send(embed=embed)
            else:
                author = await self.economy.get_member(ctx.author)
                if author.money <= 0:
                    await ctx.send(f"{self.bot.warning} | You can't send {self.format_money(author.money)} to someone!")
                else:
                    await self.economy.add_balance(member, author.money)
                    await self.economy.deduct_balance(ctx.author, author.money)
                    embed = self.make_embed(ctx.author, author.money, f"{self.bot.success} | Sent $money to {member.mention}!")
                    await ctx.send(embed=embed)
        else:
            author = await self.economy.get_member(ctx.author)
            if author.money <= 0:
                await ctx.send(f"{self.bot.warning} | You can't send {self.format_money(author.money)} to someone!")
            elif author.money < amount:
                await ctx.send(f"{self.bot.warning} | You don't have {self.format_money(amount)} in hands!")
            else:
                await self.economy.add_balance(member, amount)
                await self.economy.deduct_balance(ctx.author, amount)
                embed = self.make_embed(ctx.author, amount, f"{self.bot.success} | Sent $money to {member.mention}!")
                await ctx.send(embed=embed)



    @commands.hybrid_group(name='add', description='Use this command to add money to other members.', usage='add [money | bank] <member> <amount>')
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @app_commands.describe(member='Member whom you want to add money.', amount='Amount of money you want to send.')
    async def add(self, ctx: commands.Context, member: discord.Member, amount: int) -> None:
        
        await self.economy.add_balance(member, amount)
        embed = self.make_embed(ctx.author, amount, f"{self.bot.success} | Added $money to {member.mention}'s Cash!")
        await ctx.send(embed=embed)


    @add.command(name='money', description='Use this command to add money to other members cash.', usage='add money <member> <amount>')
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @app_commands.describe(member='Member whom you want to add money.', amount='Amount of money you want to send.')
    async def amoney(self, ctx: commands.Context, member: discord.Member, amount: int) -> None:
        
        await self.economy.add_balance(member, amount)
        embed = self.make_embed(ctx.author, amount, f"{self.bot.success} | Added $money to {member.mention}'s Cash!")
        await ctx.send(embed=embed)
    

    @add.command(name='bank', description='Use this command to add money to other members bank.', usage='add bank <member> <amount>')
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @app_commands.describe(member='Member whom you want to add money.', amount='Amount of money you want to send.')
    async def abank(self, ctx: commands.Context, member: discord.Member, amount: int) -> None:
        
        await self.economy.add_bank(member, amount)
        embed = self.make_embed(ctx.author, amount, f"{self.bot.success} | Added $money to {member.mention}'s Bank!")
        await ctx.send(embed=embed)




    @commands.hybrid_group(name='update', description='Use this command to set money of other member.', usage='update [money | bank] <member> <amount>')
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @app_commands.describe(member='Member whose money you want to update.', amount='Amount of money you want to set.')
    async def update(self, ctx: commands.Context, member: discord.Member, amount: int) -> None:
        
        await self.economy.update_balance(member, amount)
        embed = self.make_embed(ctx.author, amount, f"{self.bot.success} | Set {member.mention}'s Cash to $money!")
        await ctx.send(embed=embed)


    @update.command(name='money', description='Use this command to set money of other member.', usage='update money <member> <amount>')
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @app_commands.describe(member='Member whose money you want to update.', amount='Amount of money you want to set.')
    async def umoney(self, ctx: commands.Context, member: discord.Member, amount: int) -> None:
        
        await self.economy.update_balance(member, amount)
        embed = self.make_embed(ctx.author, amount, f"{self.bot.success} | Set {member.mention}'s Cash to $money!")
        await ctx.send(embed=embed)
    

    @update.command(name='bank', description='Use this command to set bank money of member.', usage='update bank <member> <amount>')
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @app_commands.describe(member='Member whose money you want to update.', amount='Amount of money you want to set.')
    async def ubank(self, ctx: commands.Context, member: discord.Member, amount: int) -> None:
        
        await self.economy.update_bank(member, amount)
        embed = self.make_embed(ctx.author, amount, f"{self.bot.success} | Set {member.mention}'s Bank money to $money!")
        await ctx.send(embed=embed)


    @commands.hybrid_command(name='rob', description='Robs a member with risk of getting caught.', usage='rob <member>')
    @commands.guild_only()
    @app_commands.describe(member='Member whom you want to rob.')
    async def rob(self, ctx: commands.Context, member: discord.Member) -> None:

        if member.bot:
            await ctx.send(f'{self.bot.warning} | You should not rob poor machines.')
            return
        elif member == ctx.author:
            await ctx.send(f'{self.bot.warning} | You can not rob your self.')
            return
        
        member_economy: EconomyMember = await self.economy.get_member(member)
        author_economy: EconomyMember = await self.economy.get_member(ctx.author)
        author_networth: int = author_economy.money + author_economy.bank

        if member_economy.money < 2000:
            await ctx.send(f"{self.bot.warning} | {member} doesn't have much money in hands to rob for :(")
            return
        
        if author_networth < 1000:
            await ctx.send(f"{self.bot.warning} | You currently don't have enough networth to perform this action!")
            return
        
        success: int = random.choice([1, -1])
        percent: int = random.randint(30, 90) # Members can gain or lose between 30%-90% 

        if success < 0:
            fine: int = self.percentage(author_networth, percent) # Fine should be taken from networth

            embed = self.make_embed(ctx.author, fine * -1, f"You got caught robbing {member.mention}, you payed them a fine of $money.")

            await self.economy.add_balance(member, fine)
            await self.economy.deduct_balance(ctx.author, fine)

        else:
            amount: int = self.percentage(member_economy.money, percent) # Money in hand can only be robbed

            embed = self.make_embed(ctx.author, amount, f"You successfully robbed {member.mention}, you took total of $money.")

            await self.economy.add_balance(ctx.author, amount)
            await self.economy.deduct_balance(member, amount)

        await ctx.send(embed=embed)




    @commands.hybrid_command(name="leaderboard", description="Display economy leaderboard.", aliases=["lb"], usage="leaderboard [page]")
    @commands.guild_only()
    @app_commands.describe(page="Page of the leaderboard.")
    async def leaderboard(self, ctx: commands.Context, page: int = 1) -> None:
        
        data = await self.economy.get_members(ctx.guild)

        max_pages = len(data)//10
        if max_pages <= len(data)/10:
            max_pages += 1
        
        if page < 0 or page > max_pages or not data:
            return await ctx.send(f"{self.bot.fail} | Page **{page}** not found.")
        
        
        entries = []

        for rank, member in enumerate(data, start=1):
            sentence = f"{rank}. <@{member.user_id}>:\t {self.format_money(member.bank + member.money)}"
            entries.append(sentence)

        
        view = Controller(ctx, entries, page, max_pages)
        embed = view.make_page()
        view.set_view()
        view.message = await ctx.send(embed=embed, view=view)

    
async def setup(bot: 'Bot') -> None:
    await bot.add_cog(Economy(bot))