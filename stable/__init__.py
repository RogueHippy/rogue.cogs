from .image_generation import ImageGeneration

def setup(bot):
    bot.add_cog(ImageGeneration(bot))
