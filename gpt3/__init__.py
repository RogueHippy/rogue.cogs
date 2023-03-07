from redbot.core.bot import Red
from .gpt3 import GPT3

async def setup(bot: Red):
    cog = GPT3(bot)
    bot.add_cog(cog)
