import typing

import discord
from discord.ext import commands


class DevCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    @commands.has_guild_permissions(administrator=True)
    async def sync(self, ctx: commands.Context, guilds: commands.Greedy[discord.Object], spec: typing.Optional[typing.Literal["~", "*", "^", "x"]] = None) -> None:
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

            await ctx.send(
                f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
            )
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
    @commands.has_guild_permissions(administrator=True)
    async def test(self, ctx):
        print(self.bot.guild_settings)
        print(self.bot.guild_settings[ctx.guild.id]['join']['channel_id'])

async def setup(bot: commands.Bot):
    await bot.add_cog(DevCommands(bot))
