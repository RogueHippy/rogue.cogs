import pkg_resources

try:
    pkg_resources.require("openai==0.27.0")
except pkg_resources.VersionConflict:
    print("The required version of requests is not installed")
    exit(1)

import openai
import os
import discord
import logging
import asyncio
from redbot.core import data_manager
from redbot.core import commands
from redbot.core import checks
from redbot.core.bot import Red
from redbot.core.config import Config


class chatGPT(commands.Cog):
    def __init__(self, bot: Red) -> None:
        self.prompt = ""
        self.response = ""
        self.bot = bot
        self.log = logging.getLogger('red.rogue.chatGPT')
        self.config = Config.get_conf(
            self,
            identifier=365398642334499908
        )
        self.user_threads = {}
        defaultGlobalConfig = {
            "tokenLimit": 2500
        }
        defaultGuildConfig = {
            "channels": [],
            "replyRespond": True
        }
        self.config.register_global(**defaultGlobalConfig)
        self.config.register_guild(**defaultGuildConfig)

    async def send_message(self, user_id, message, model, tokenLimit):
        if user_id not in self.user_threads:
            self.user_threads[user_id] = ""
        self.prompt = self.user_threads[user_id]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": self.prompt},
            ],
            #prompt=self.prompt + message,
            max_tokens=tokenLimit,
            stop=None,
            temperature=0.7,
        )
        self.user_threads[user_id] = response["choices"][0]["text"]
        return self.user_threads[user_id]

    async def send_chat(self, ctx: commands.Context, query: str):
        async with ctx.typing():
            try:
                model = await self.config.model()
                tokenLimit = await self.config.tokenLimit()
                messages = [
                    {"role": "system", "content": query},
                ]
                #self.log.info("Sending query: `" + query + "` to chatGPT. With model: " + model)
                chatGPTKey = await self.bot.get_shared_api_tokens("openai")
                if chatGPTKey.get("api_key") is None:
                    self.log.error("No api key set.")
                    return await ctx.send(
                        "The bot owner still needs to set the openai api key using `[p]set api openai  api_key,<api key>`. It can be created at: https://beta.openai.com/account/api-keys")
                openai.api_key = chatGPTKey.get("api_key")
                response: str = await self.send_message(ctx.author.id, query, model, tokenLimit)
                if len(response) > 0 and len(response) < 2000:
                    self.log.info("Response is under 2000 characters and is: `" + response + "`.")
                    await ctx.reply(response)
                elif len(response) > 2000:
                    self.log.info(
                        "Response is over 2000 characters sending as file attachment. Response is: `" + response + "`.")
                    with open(str(ctx.author.id) + '.txt', 'w') as f:
                        f.write(response)
                    with open(str(ctx.author.id) + '.txt', 'r') as f:
                        await ctx.send(file=discord.File(f))
                        os.remove(f)
                else:
                    await ctx.reply(
                        "I'm sorry, for some reason chatGPT's response contained nothing, please try sending your query again.")
            except openai.error.InvalidRequestError as err:
                await ctx.send(err)

    @commands.Cog.listener()
    async def on_message_without_command(self, message: discord.Message):
        whitelistedChannels: list = await self.config.guild(message.guild).channels()
        replyRespond: bool = await self.config.guild(message.guild).replyRespond()
        query = message.content
        validFile: bool = False
        validFileTypes = ['.py', '.js', '.txt', '.yaml', '.html', '.xml', '.c', '.java', '.cs', '.php', '.css']
        ctx = await self.bot.get_context(message)
        if whitelistedChannels is not None and message.channel.id in whitelistedChannels and message.author.id != self.bot.user.id:
            if message.attachments:
                # Get the file
                self.log.debug("Message has a file, is it valid?")
                file: discord.Attachment = message.attachments[0]
                for filetype in validFileTypes:
                    if file.filename.endswith(filetype):
                        self.log.debug("It is valid.")
                        fileContents = await file.read()
                        query = query + "\n" + str(fileContents)
                        self.log.debug("Final query: " + query)
                        validFile = True
                if not validFile:
                    await ctx.reply("Sorry but that isn't a valid filetype.")
            await self.send_chat(ctx, query)
        if replyRespond and message.reference is not None and message.author.id != self.bot.user.id:
            # Fetching the message
            channel = self.bot.get_channel(message.reference.channel_id)
            msg = await channel.fetch_message(message.reference.message_id)
            context: commands.Context = await self.bot.get_context(msg)
            if context.author.id == self.bot.user.id:
                await self.send_chat(ctx, query)

    @commands.group(name="chatgpt")
    async def chatgpt(self, ctx: commands.Context):
        """
        Base command for chatgpt related commands
        """
        pass

    @chatgpt.command(name="chat")
    async def chat(self, ctx: commands.Context, *, query: str):
        """
        Asks chatgpt a query
        """
        await self.send_chat(ctx, query)

    @checks.guildowner()
    @chatgpt.command(name="channellist")
    async def channellist(self, ctx: commands.Context):
        """
        Lists the channels currently in the whitelist
        """
        currentChannels: list = await self.config.guild(ctx.guild).channels()
        if currentChannels is not None:
            message = "The current channels are:\n"
            for channelId in currentChannels:
                message = message + "<#" + str(channelId) + ">\n"
            await ctx.reply(message)
        else:
            await ctx.reply("There are currently no channels whitelisted for chatGPT.")

    @checks.guildowner()
    @chatgpt.command(name="set")
    async def set(self, ctx: commands.Context, setting: str, value):
        """
        Changes settings for bot to use

        Use `[p]chatgpt set channeladd <channel_id>` or `[p]chatgpt set channelremove <channel_id>` to set up channel whitelist where the bot will respond.\n\n
        Use `[p]chatgpt set replyRespond <True or False>` to enable or disable the bot responding to replies regardless of channel
        """
        if setting == "channeladd":
            if value is discord.TextChannel:
                value: int = value.id
                pass
            channelId = int(value)
            channel = self.bot.get_channel(channelId)
            if channel == None:
                await ctx.reply("That channel does not exist or the bot can not see it.")
                return
            elif channel.guild != ctx.guild:
                await ctx.reply("That channel isn't in this server...")
                return
            currentChannels: list = await self.config.guild(ctx.guild).channels()
            self.log.info(currentChannels)
            if currentChannels is None:
                self.log.info("Current channel list is empty adding the new channel.")
                newChannels: list = [channelId]
                await ctx.reply("<#" + str(channelId) + "> is now whitelisted.")
                await self.config.guild(ctx.guild).channels.set(newChannels)
                return
            if channelId not in currentChannels:
                self.log.info("Channel is not in list so we add it.")
                currentChannels.append(channelId)
                self.log.info(currentChannels)
                await ctx.reply("<#" + str(channelId) + "> is now whitelisted.")
                await self.config.guild(ctx.guild).channels.set(currentChannels)
                return
            await ctx.reply("<#" + str(channelId) + "> was already whitelisted.")

        elif setting == "channelremove":
            if value is discord.TextChannel:
                value: int = value.id
                pass
            currentChannels: list = await self.config.guild(ctx.guild).channels()
            try:
                currentChannels.remove(int(value))
                await self.config.guild(ctx.guild).channels.set(currentChannels)
                await ctx.reply("<#" + str(value) + "> is no longer whitelisted.")
            except ValueError:
                await ctx.reply("That channel was already not in channel list.")

        elif setting == "replyRespond":
            if value is str:
                value = value.lower()
            if value == "true" or value == "1":
                await self.config.guild(ctx.guild).replyRespond.set(True)
                await ctx.reply("replyRespond is now set to True")
            elif value == "false" or value == "0":
                await self.config.guild(ctx.guild).replyRespond.set(False)
                await ctx.reply("replyRespond is now set to False")
            else:
                await ctx.reply("This command only accepts `true` or `false`.")

    @checks.is_owner()
    @chatgpt.command(name="model")
    async def model(self, ctx: commands.Context, model: str):
        """
        Allows the changing of model chatbot is running. Options are: 0-`text-ada-001` 1-`text-babbage-001` 2-`text-curie-001` 3-`text-davinci-002` 4-`text-davinci-003` current-`shows current model`\n\n

        For more information on what this means please check out: https://beta.openai.com/docs/models/gpt-3
        """
        model_map = {
            "0": "text-ada-001",
            "1": "text-babbage-001",
            "2": "text-curie-001",
            "3": "text-davinci-002",
            "4": "text-davinci-003",
            "text-ada-001": "text-ada-001",
            "text-babbage-001": "text-babbage-001",
            "text-curie-001": "text-curie-001",
            "text-davinci-002": "text-davinci-002",
            "text-davinci-003": "text-davinci-003"
        }
        if model in model_map:
            await self.config.model.set(model_map[model])
            await ctx.reply("The chatbot model is now set to: `" + model_map[model] + "`")
        elif model == "current":
            currentModel = await self.config.model()
            await ctx.reply("The chatbot model is currently set to: " + currentModel)
        else:
            await ctx.reply("That is not a valid model please use `[p]chatgpt model` to see valid models")

    @checks.is_owner()
    @chatgpt.command(name="tokenlimit")
    async def tokenlimit(self, ctx: commands.Context, tokenLimit: int):
        """
        Allows for changing the max amount of tokens used in one query, default is 1000. Token cost is counted as query + response. Every model has a max cost of 2048 with the exception of the davinci models which have a max of 4000\n\n

        For more information on tokens check out: https://beta.openai.com/docs/models/gpt-3
        For token prices also see: https://openai.com/api/pricing/
        """
        model = await self.config.model()
        model_limits = {
            "text-ada-001": (0, 2048),
            "text-babbage-001": (0, 2048),
            "text-curie-001": (0, 2048),
            "text-davinci-002": (0, 4000),
            "text-davinci-003": (0, 4000)
        }

        if model in model_limits and model_limits[model][0] < tokenLimit <= model_limits[model][1]:
            await self.config.tokenlimit.set(tokenLimit)
            await ctx.reply("Token limit is now set to " + str(tokenLimit))
        else:
            await ctx.reply("That is not a valid token amount.")
