import discord
import requests
from redbot.core import commands, Config
from io import BytesIO
from discord.ext import commands

class ImageGeneration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def generate_image(self, ctx, text):
        response = requests.get(f"https://api.stable.diffusion.com/v1/image/generate?text={text}")
        image = BytesIO(response.content)
        await ctx.send(file=discord.File(image, "image.png"))
