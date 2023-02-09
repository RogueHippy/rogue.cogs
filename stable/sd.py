import requests
from redbot.core import commands

class ImageGenerator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = None

    @commands.group(name="imagegen")
    async def imagegen(self, ctx):
        """Image generation using the stability-ai/stable-diffusion API."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid subcommand passed.")
    
    @imagegen.command(name="setkey")
    async def set_api_key(self, ctx, api_key: str):
        """Set the API key for the stability-ai/stable-diffusion API."""
        self.api_key = api_key
        await ctx.send("API key set successfully.")
    
    @imagegen.command(name="generate")
    async def generate_image(self, ctx, input_text: str):
        """Generate an image using the stability-ai/stable-diffusion API."""
        if self.api_key is None:
            await ctx.send("API key not set. Please set the API key using `imagegen setkey`.")
            return

        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        data = {
            "prompt": input_text
        }
        response = requests.post("https://api.stability.ai/stable-diffusion/v1/images", headers=headers, json=data)
        if response.status_code == 200:
            image_url = response.json()["url"]
            await ctx.send(image_url)
        else:
            await ctx.send("Failed to generate image. Please check your API key and input.")

def setup(bot):
    bot.add_cog(ImageGenerator(bot))
