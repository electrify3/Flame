import discord

from abc import ABC, abstractmethod
from typing import Sequence

from discord.ui import View
from discord.ext import commands


class Paginator(View, ABC):
    def __init__(self, ctx: commands.Context, items: Sequence, page: int, max_pages: int) -> None:
        super().__init__(
        timeout = 120
        )
        self.ctx: commands.Context = ctx
        self.page: int = page
        self.items: Sequence = items
        self.message: discord.Message | None = None
        self.max_pages: int = max_pages
    
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.ctx.author:
            await interaction.response.send_message(f"{interaction.client.warning} | You don't own this session!", ephemeral=True)
            return False
        else:
            return True
    
    
    async def on_timeout(self) -> None:
        for children in self.children:
            if not (hasattr(children, "label") and children.label):
                children.disabled = True
        await self.message.edit(view=self)
    
    
    def set_view(self) -> None:

        config: bool = False if self.max_pages != 1 else True
        
        if self.page == 1:
            self.children[0].disabled = True
            self.children[1].disabled = True
            self.children[3].disabled = config
            self.children[4].disabled = config
        elif self.page == self.max_pages:
            self.children[0].disabled = config
            self.children[1].disabled = config
            self.children[3].disabled = True
            self.children[4].disabled = True
        else:
            self.children[0].disabled = False
            self.children[1].disabled = False
            self.children[3].disabled = False
            self.children[4].disabled = False
    

    @abstractmethod
    def make_page(self) -> discord.Embed:
        pass
    
    
    @discord.ui.button(emoji="<:Edoublearrow2:1180724072678694962>")
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.defer()
        self.page = 1
        self.set_view()
        em = self.make_page()
        await interaction.message.edit(embed=em, view=self)
        
    
    @discord.ui.button(emoji="<:Earrow2:1180723707279315057>")
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.defer()
        self.page -= 1
        self.set_view()
        em = self.make_page()
        await interaction.message.edit(embed=em, view=self)
        
    
    @discord.ui.button(emoji="<:Edelete:1158793677712392213>")
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.defer()
        self.stop()
        await interaction.message.delete()
        
    
    @discord.ui.button(emoji="<:Earrow:1127175875549462602>")
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.defer()
        self.page += 1
        self.set_view()
        em = self.make_page()
        await interaction.message.edit(embed=em, view=self)
    
    
    @discord.ui.button(emoji="<:Edoublearrow:1180723248388902933>")
    async def end(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.defer()
        self.page = self.max_pages
        self.set_view()
        em = self.make_page()
        await interaction.message.edit(embed=em, view=self)