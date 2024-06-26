import asyncio
import typing

import discord
from discord.ext import commands

from config.settings import DEVELOPER_IDS


class DevCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def execute_command(self, command: str):
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await proc.communicate()

        content = f'**{command!r}** exited with return code: {proc.returncode}'
        if stdout:
            content += f'\n**stdout**\n```{stdout.decode()}```'
        if stderr and not command.startswith('git'):
            content += f'\n\n**stderr**\n```{stderr.decode()}```'

        return content

    @commands.command()
    async def sync(self, ctx: commands.Context, guilds: commands.Greedy[discord.Object], spec: typing.Optional[typing.Literal["~", "*", "^", "x"]] = None) -> None:
        if ctx.author.id not in DEVELOPER_IDS:
            return

        if not guilds:
            if spec == "~":
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "*":
                ctx.bot.tree.copy_global_to(guild=ctx.guild)
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "^":
                ctx.bot.tree.clear_commands(guild=ctx.guild)
                await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "x":
                ctx.bot.tree.clear_commands(guild=None)
                await ctx.bot.tree.sync()
                await ctx.send(f"Cleared commands for {ctx.guild}")
                return
            else:
                synced = await ctx.bot.tree.sync()

            await ctx.send(f'Synced {len(synced)} commands {"globally" if spec is None else "to the current guild."}')
            return

        ret = 0
        for guild_item in guilds:
            try:
                await ctx.bot.tree.sync(guild=guild_item)
            except discord.HTTPException:
                pass
            else:
                ret += 1

        await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

        # Greedy -> commands.Greedy
        # Context -> commands.Context (or your subclass)
        # Object -> discord.Object
        # typing.Optional and typing.Literal

        # Works like:
        # !sync -> global sync
        # !sync ~ -> sync current guild
        # !sync * -> copies all global app commands to current guild and syncs
        # !sync ^ -> clears all commands from the current guild target and syncs (removes guild commands)
        # !sync id_1 id_2 -> syncs guilds with id 1 and 2

    @commands.command()
    async def pull(self, ctx: commands.Context):
        if ctx.author.id not in DEVELOPER_IDS:
            content = await self.execute_command('git pull')
            await ctx.send(content)
            await ctx.message.delete()

    @commands.command()
    async def restart(self, ctx: commands.Context):
        if ctx.author.id not in DEVELOPER_IDS:
            content = await self.execute_command('systemctl restart')
            await ctx.send(content)
            await ctx.message.delete()

    @commands.command()
    async def stop(self, ctx: commands.Context):
        if ctx.author.id not in DEVELOPER_IDS:
            content = await self.execute_command('systemctl stop')
            await ctx.send(content)
            await ctx.message.delete()

async def setup(bot: commands.Bot):
    await bot.add_cog(DevCommands(bot))
