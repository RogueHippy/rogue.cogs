from .mycog import MyCog


async def setup(bot):
    await bot.add_cog(MyCog(bot))
