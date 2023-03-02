from redbot.core.bot import Red

from .openai import openai

#with open(Path(__file__).parent / "info.json") as fp:
#    __red_end_user_data_statement__ = json.load(fp)["end_user_data_statement"]


async def setup(bot: Red) -> None:
    bot.add_cog(openai(bot))
