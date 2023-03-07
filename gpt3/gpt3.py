import openai
from redbot.core import commands

openai.api_key = "YOUR_API_KEY_HERE"

class GPT3(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_threads = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        user_id = message.author.id
        if user_id not in self.user_threads:
            self.user_threads[user_id] = ""
        prompt = f"{self.user_threads[user_id]}{message.content}\nGPT3:"
        try:
            response = openai.Completion.create(
                engine="davinci",
                prompt=prompt,
                max_tokens=1024,
                n=1,
                stop=None,
                temperature=0.5,
            )
            text = response.choices[0].text
            self.user_threads[user_id] = f"{message.content}\n{text}"
            await message.channel.send(text)
        except openai.Error as e:
            await message.channel.send(f"An error occurred: {e}")
