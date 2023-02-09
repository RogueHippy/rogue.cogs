import requests
from redbot.core import commands

class ImageGeneration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def generate_image(self, ctx, text: str):
        api_url = "https://api.stable.zip/v1/images/generate"
        params = {"text": text}
        response = requests.get(api_url, params=params)
        if response.status_code == 200:
            image_url = response.json().get("url")
            await ctx.send(image_url)
        else:
            await ctx.send("Failed to generate image.")

def setup(bot):
    bot.add_cog(ImageGeneration(bot))
