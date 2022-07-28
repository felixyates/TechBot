import discord
from modules import db, vars, embs

class Server():

    def __init__(self, guild):
        if isinstance(guild, discord.guild.Guild):
            for attr in dir(guild):
                if not attr.startswith('_'):
                    if hasattr(guild, attr):
                        value = getattr(guild, attr)
                        setattr(self, attr, value)
            self.ownerID: str(self.owner.id)
        elif isinstance(guild, int) or isinstance(guild, str):
            self.id = str(guild)
    
    async def Fetch(self, bot: discord.Bot):
        self.__init__(await bot.fetch_guild(self.id))
    
    async def Fetch_DB(self):
        "Fetches server information from database"
        row = await db.load(self.id)
        print(row)
    
    async def Exists_DB(self):
        "Checks if server exists in database"
        if len(await db.load(self.id) > 0):
            return True
        return False

    async def Create(self, type: int):
        await db.modify(f"INSERT INTO servers VALUES(?, ?, ?)", (self.id, self.name, self.ownerID))
        await self.Message(type)
        await self.guild.text_channels[0].send(embed = embs.Join())
    
    async def Delete(self, type: int):
        await db.modify(f'DELETE FROM servers WHERE id = ?', self.id,)
        await self.Message(type)

    async def Message(self, type: int):
        """Sends message to channel specified in variables module.
        Details server name, owner, and member count.
        
        Type 1: `+ Joined`
        Type 2: `- Left`
        Type 3: `+ While bot was offline, joined`
        Type 4: `- While bot was offline, left`"""

        if hasattr(self, 'guild'):
            serversChannel = self.bot.get_channel(vars.botServersChannel)
            types = ["+ Joined", "- Left", "+ While bot was offline, joined", "- While bot was offline, left"]
            beginning = types[type]

            if hasattr(self.guild, 'approximate_member_count'):
                message = f"{beginning} `{guild.name}` - `{guild.approximate_member_count}` members; owned by `{guild.owner.mention}`."
            else: 
                guild = self.bot.get_guild(guild)
                message = f"{beginning} `{guild.name}` - `unknown` members; owned by `{guild.owner.mention}`."

            await serversChannel.send(message)

    async def GetModules(self):
        moduleNames = ['welcome', 'music', 'slurdetector', 'textresponder']
        for name in moduleNames:
            module = await self.Module(name).Get(self.id)
            setattr(self, name, module)
    
    async def GetModule(self, module: str):
        module = await self.Module(module).Get(self.id)
        return module
    
    async def GetEmbed(self):
        await self.GetModules()
        serverEmbed = embs.Embed(title = f"{self.name}: {self.id}", thumbnail = self.icon.url)
        fields = [
            ["Slur Detector", f"{self.slurdetector.state}, <#{self.slurdetector.channel}>"],
            ["Music", f"{self.music.state}, <#{self.music.channel}>"],
            [
                "Welcome",
                f"""{self.welcome.state}, <#{self.welcome.channel}>, {self.welcome.message}"""
            ]
        ]
        serverEmbed.AddFields(fields, inline = False)
        return serverEmbed
    
    class Module:
        state = -1
        channel = ""

        def __init__(self, name: str):
            self.name = name

        async def Get(self, guild_id: str):
            self.guild_id = str(guild_id)
            module = await db.loadModule(guild_id, self.name)
            for (key, value) in module.items():
                setattr(self, key, value)
            return self

        def IsEnabled(self) -> bool:
            if self.state == 1:
                return True
            return False
        
        async def Enable(self) -> dict:
            "Sets the state of the module to enabled"
            return await self.SetState(1)
        
        async def Disable(self) -> dict:
            "Sets the state of the module to disabled"
            return await self.SetState(0)

        async def SetState(self, state: int) -> dict:
            return await db.updateModule(
                guild_id = self.guild_id,
                module = self.name,
                attribute = "state",
                value = state
            )

        async def SetChannel(self, channel: discord.TextChannel) -> dict:
            return await db.updateModule(
                guild_id = self.guild_id,
                module = self.name,
                attribute = "channel_id",
                value = str(channel.id)
            )

        async def SetMessage(self, message: str) -> dict:
            if hasattr(self, "message"):
                return await db.updateModule(
                    guild_id = self.guild_id,
                    module = self.name,
                    attribute = "message",
                    value = message
                )
            else:
                print(f"!!! {self.name} module does not have a message attribute !!!")
