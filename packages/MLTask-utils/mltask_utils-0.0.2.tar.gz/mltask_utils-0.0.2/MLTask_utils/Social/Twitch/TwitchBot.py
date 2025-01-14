from twitchio.ext import commands
from pprint import pprint


class TwitchBot(commands.Bot):
    def __init__(self, access_token, initial_channels):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        super().__init__(token=access_token,
                         prefix='/', initial_channels=initial_channels)

    async def event_ready(self):
        # We are logged in and ready to chat and use commands...
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')

    async def event_message(self, message):
        # Messages with echo set to True are messages sent by the bot...
        # For now we just want to ignore them...
        if message.echo:
            return

        # Print the contents of our message to console...
        # pprint(
        #     f'{message.author.display_name} said: {message.content} @ {message.timestamp}')

        # Since we have commands and are overriding the default `event_message`
        # We must let the bot know we want to handle and invoke our commands...
        await self.handle_commands(message)

    async def event_usernotice_subscription(self, metadata):
        pprint(metadata)

    @commands.command()
    async def hello(self, ctx: commands.Context):
        # Send a hello back!
        print("received command")
        pprint(ctx)
        # await ctx.send(f'Hello {ctx.author.name}!')
