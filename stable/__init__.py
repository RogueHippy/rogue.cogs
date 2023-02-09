from .image_generator import ImageGenerator

def setup(bot):
    bot.add_cog(ImageGenerator(bot))
