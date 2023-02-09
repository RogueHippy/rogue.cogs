import requests
import json
import discord
from discord.ext import commands

class OpenAICog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.model = "text-davinci-003"
        self.api_key = ""  # Add your OpenAI API key here

    @commands.group(name="openai", invoke_without_command=True)
    async def openai_group(self, ctx, *, prompt: str):
        response = requests.post(
            "https://api.openai.com/v1/engines/{}/jobs".format(self.model),
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(self.api_key)
            },
            data=json.dumps({
                "prompt": prompt,
                "max_tokens": 1024,
                "n": 1,
                "stop": None,
                "temperature": 0.5
            })
        )
        response.raise_for_status()
        result = response.json()
        answer = result["choices"][0]["text"].strip()
        await ctx.send(answer)

    @openai_group.command(name="key")
    async def openai_key(self, ctx, key: str):
        self.api_key = key
        await ctx.send(f"OpenAI API key set to `{key}`")
