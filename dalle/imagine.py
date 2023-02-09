import discord
import requests
from redbot.core import commands, Config
from io import BytesIO
class Imagine(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=5867382938)
        self.config.register_global(api_key=None)
    
    @commands.group(name="dalle")
    async def imagine(self, ctx):
        """Generate images using the Dall-E 2 API"""
        pass
    
    @imagine.command(name="key")
    async def set_api_key(self, ctx, api_key: str):
        """Set the Dall-E 2 API key"""
        await self.config.api_key.set(api_key)
        await ctx.send("Dall-E 2 API key set successfully")

    @imagine.command(name="image")
    async def generate_image(self, ctx, *, prompt: str):
        """Generate an image from a prompt using Dall-E 2 API"""
        api_key = await self.config.api_key()
        if not api_key:
            return await ctx.send("Please set the Dall-E 2 API key using the `imagine key` command")

        async with ctx.typing():
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            data = {
                "prompt": prompt,
                "model": "image-alpha-001",
                "num_images":1,
                "size":"1024x1024"
            }
            response = requests.post("https://api.openai.com/v1/images/generations", headers=headers, json=data)
        if response.status_code == 200:
            image_url = response.json()['data'][0]['url']
            response = requests.get(image_url)
            if response.status_code == 200:
                file = discord.File(fp=BytesIO(response.content), filename="image.jpg")
                await ctx.send(file=file)
            else:
                await ctx.send("Failed to retrieve image")
        else:
            await ctx.send("Failed to generate image, please check the API key and prompt")
