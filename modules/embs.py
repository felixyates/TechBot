import discord, datetime
from modules import vars, emoji

support = ["Get Support", "Need help, or want to report a bug? Join the [support server](https://www.techlifeyt.com/techbot) for help.", False]

class Embed(discord.Embed):
    def __init__(self, **kwargs):
        new_kwargs = kwargs

        if kwargs.get("thumbnail") is not None:
                super().set_thumbnail(url = kwargs['thumbnail'])
                new_kwargs.pop('thumbnail')

        super().__init__(**new_kwargs)

    def AddFields(self, fields: "list[list]", inline = True):
        for field in fields:
            if len(field) == 3:
                inline = field[2]
            super().add_field(name = field[0], value = field[1], inline = inline)
    
    def ByFooter(self, author: discord.User, text: str):
        "Sets the footer to [text] by [username]"
        super().set_footer(text = f"{text} by {author.display_name}", icon_url = author.avatar.url)

    def RequestedByFooter(self, author: discord.User):
        self.ByFooter(author, "Requested")
    
    def TimestampFooter(self, text: str = ""):
        self.timestamp = datetime.datetime.utcnow()
        if text != "":
            super().set_footer(text = text)

class Join(Embed):
    "Sent in the first channel of the server when the bot is added (see listeners.py)"
    title = f"{emoji.wave_animated} Heeeere's {vars.BOTNAME}!"
    description = f"Thank you for adding {vars.BOTNAME}. If you run into any errors, or need any help, please make sure to join the [support server](https://techlifeyt.com/techbot)."
    def __init__(self):
        super().__init__(title = self.title, description = self.description)
        super().set_author(
            name = "TechLife",
            icon_url = "https://www.techlifeyt.com/wp-content/uploads/2021/06/TechLife-PFP-128x.gif",
            url = "https://techlifeyt.com/links"
        )

class Online(Embed):
    "Sent when the bot comes online (see listeners.py)"
    title = f"{emoji.online} Online"
    description = f"{vars.botName} is back online and reporting for duty!"
    color = discord.Color.green()
    def __init__(self):
        super().__init__(title = self.title, description = self.description, color = self.color)

class Maintenance(Embed):
    "Sent when maintenance mode is enabled (see owner.py)"
    title = f'{emoji.dnd} Maintenance'
    description = f"""{vars.BOTNAME} is currently undergoing maintenance.
    This means that most, if not all, commands will be unavailable.
    Check back here for updates."""
    color = discord.Color.red()
    def __init__(self):
        super().__init__(title = self.title, description = self.description, color = self.color)
        self.TimestampFooter("Maintenance started")

class Offline(Embed):
    "Sent when the bot logs out (see owner.py)"
    title = f'{emoji.offline} Offline'
    description = f"{vars.BOTNAME} is going offline. Check here for updates."
    def __init__(self):
        super().__init__(title = self.title, description = self.description)
        self.TimestampFooter("Last online")

class Success(Embed):
    "Sent when a command executes successfully"
    title = 'Success!'
    color = discord.Color.green()
    def __init__(self, description):
        description = f"{emoji.yep} " + description
        super().__init__(title = self.title, description = description, color = self.color)

class Failure(Embed):
    "Sent when a command fails, but the error does not need to be logged/reported"
    title = 'Uh oh!'
    color = discord.Color.red()
    def __init__(self, description, exception: Exception = None):    
        description = f"{emoji.nope} " + description
        super().__init__(title = self.title, description = description, color = self.color)
        if exception is not None:
            self.AddFields([['Error', f'`{exception}`'], support])

class Help(Embed):
    "Sent when the help command is invoked"
    url = "https://www.techlifeyt.com/techbot-commands"
    title = 'Commands'
    description = f"""The link above will take you to a table with all of TechBot's commands.
        Regular commands are no longer supported. Please use slash commands instead."""
    def __init__(self, author: discord.User):
        super().__init__(title = self.title, description = self.description, url = self.url)
        super().set_author(
            name = 'TechLife',
            url = 'https://www.techlifeyt.com/links',
            icon_url = 'https://www.techlifeyt.com/wp-content/uploads/2020/04/cropped-TechLife-150x150-1.png'
        )
        super().add_field(name = "Get Support", value="Need help, or want to report a bug? Join the [support server](https://www.techlifeyt.com/techbot) for help.")
        self.TimestampFooter()
        self.RequestedByFooter(author)