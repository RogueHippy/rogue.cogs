from .openai_cog import OpenAICog

def setup(bot):
    bot.add_cog(OpenAICog(bot))
