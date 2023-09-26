from .rcon import RedCon

async def setup(bot):
    await bot.add_cog(RedCon(bot))
