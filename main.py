# -*- coding: utf-8 -*-
"""
Importing packages needed for the bot to function,
"""
from datetime import datetime
from configparser import ConfigParser
from twitchio.ext import commands
from twitchio.ext.commands.errors import MissingRequiredArgument
from db import DB
from config import Config


class Bot(commands.Bot):
    """
    The core of the bot where it handles messages, Exceptions.

    TODO:
        Set up Cogs to split and handle commands better.
        Write better documentation.
    """

    def __init__(self, twitch_config):

        self.twitch_token = twitch_config.twitch_token
        self.twitch_prefix = twitch_config.twitch_prefix
        self.twitch_initial_channels = twitch_config.twitch_initial_channels
        self.welcome_cooldown = twitch_config.welcome_cooldown
        # Initialise our Bot with our access token, prefix, and a list of channels to join on boot...
        # prefix can be a callable, which returns a list of strings or a string...
        # initial_channels can also be a callable which returns a list of strings...
        super().__init__(token=self.twitch_token, prefix=self.twitch_prefix,
                         initial_channels=self.twitch_initial_channels)

    async def event_ready(self):
        # Notify us when everything is ready!
        # We are logged in and ready to chat and use commands...
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')

    async def event_message(self, message):
        """
        Reading chat messages and sending events if commands are found
        :param message:
        :return:
        """
        # Messages with echo set to True are messages sent by the bot...
        # For now, we just want to ignore them...
        if message.echo:
            return

        # Print the contents of our message to console...
        print(message.content, message.author.id)

        await self.handle_commands(message)

        # Checking if user is in db
        await self.welcome_message(message.author.name, message)
        await self.shoutout_message(message.author.name, message)

    async def event_command_error(self, ctx, error):
        """
        Handler for command errors
        :param ctx: Context
        :param error: What error is raised
        :return: Nothing
        """
        if isinstance(error, commands.CommandNotFound):
            # await ctx.send("Command not recognized. Please use valid commands.")
            pass
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Command not recognized, please use: !welcome add/edit/remove <username> <custom_message>")
        else:
            pass
            # Handle other exceptions here if needed
            # print(f"An error occurred: {error}")

    @commands.command()
    async def welcome(self, ctx, command=None, name=None, *, custom_message=None):
<<<<<<< HEAD
        """
        Function to Remove/Add/Edit users to Welcome message system

        Args:
            :param ctx: Context from message in chat
            :param command: Remove/Add/Edit
            :param name: Name for user
            :param custom_message: Picks up any after name
        :return: Nothing
        """
=======
>>>>>>> master
        user = ctx.author.is_mod
        if user:
            if not command:
                raise MissingRequiredArgument("name and custom_message")

            if command.lower() == "remove":
                result = db.remove_user(name)
                if result:
                    # print(result)
                    await ctx.send(f"{name} is successfully removed")
                else:
                    await ctx.send(f"{name} is not recognised or added to welcome list")
                return

            if not name or not custom_message:
                raise MissingRequiredArgument("name and custom_message")

            if command.lower() == "add":

                if name.startswith('@'):
                    name = name[1:]

                result = db.add_user(name)
                if not result:
                    await ctx.send("User already exist")
                    return
<<<<<<< HEAD
                db.set_custom_message(custom_message, name)
=======
                db.set_custommessage(custom_message, name)
>>>>>>> master
                if result:
                    await ctx.send(f"{name} added to the welcome list")

            elif command.lower() == "edit":
                # print(custom_message, name)
                result = db.set_custom_message(custom_message, name)
                if not result:
                    await ctx.send(f"{name} is not recognised or added to welcome list")
                if result:
                    await ctx.send(f"{name} new custom message is {custom_message}")

    @commands.command()
    async def toggle_shoutout(self, ctx, name):
        user = ctx.author.is_mod
        if user:
            db.toggle_shoutout(name)

    def check_time_difference(self, message_author, type):
        """
        Checking if the user has waited long enough for Welcome message to be sent
        :param type: what type of type check, if its shoutout or welcome
        :param message_author: Name of the user we are checking
        :return: True if it's true
        """
        if type == "welcome":
            timestamp_str = db.check_last_message(message_author)
        elif type == "shoutout":
            timestamp_str = db.check_last_shoutout(message_author)
        timestamp = datetime.fromisoformat(timestamp_str)
        current_time = datetime.now()

        time_difference_seconds = (current_time - timestamp).total_seconds()
        time_difference_minutes = time_difference_seconds / 60
        if time_difference_minutes > self.welcome_cooldown:
            # print(f"Time is more than 2 minutes in difference: {time_difference_minutes} minutes")
            return True

    async def shoutout_message(self, message_author, message):
        if db.check_shoutout(username=message_author):
            if self.check_time_difference(message_author=message_author, type="shoutout"):
                db.set_last_shoutout(username=message_author)
                await message.channel.send(f"!shoutout @{message_author}")

    async def welcome_message(self, message_author, message):
        """
        Here we process if the user is in DB, then if the time difference is big enough then send welcome message
        :param message_author:  Name of the user
        :param message: To send the message in the chat
        :return:
        """
        if db.check_user(message_author):

            # Checking if sufficient time has passed
            if self.check_time_difference(message_author, type="welcome"):

                # Setting new chatting time
                db.set_last_message(message_author)

                # Checking if user has a custom message, if not will use default message
                if db.check_custom_message(message_author):
                    welcome_message = db.check_custom_message(message_author)
                    await message.channel.send(welcome_message)
            else:
                # print("Not long enough")
                return


if __name__ == "__main__":
    try:
        config = Config(ConfigParser())
        config.read_config_file()
        db = DB()
        bot = Bot(config)
        bot.run()
    except Exception as e:
        print(e)
        input("Press enter to close...")
