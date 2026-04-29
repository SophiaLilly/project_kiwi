# dsc.py

# Local Imports
from modules.llm_funcs import llm

# Partial Imports
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from typing import Final

# Full Imports
import discord
import logging
import os
import traceback


load_dotenv()

TOKEN: Final[str] = os.getenv("KIWI_DISCORD_TOKEN", "")
COMMAND_PREFIX: Final[str] = "!"


logger: logging.Logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def create_error_embed(title: str, description: str, colour: discord.Color | None = None) -> discord.Embed:
    return discord.Embed(
        title=title,
        description=description,
        color=colour or discord.Colour.blurple(),
    )


def create_bot() -> commands.Bot:
    return commands.Bot(
        command_prefix=COMMAND_PREFIX,
        intents=discord.Intents.all(),
        help_command=None,
    )


def register_events(bot: commands.Bot) -> None:

    @bot.event
    async def on_ready() -> None:
        if bot.user is not None:
            logger.info(f"Logged in as {bot.user}")
        else:
            logger.error("Bot user is None after login.")

    @bot.event
    async def on_message(message: discord.Message) -> None:
        logger.info(f"Message from channel: {message.channel} ({message.channel.id}): {message.author.global_name}: {message.content}")

        if message.author == bot.user:
            return

        if message.content.startswith(COMMAND_PREFIX):
            await bot.process_commands(message)

        acceptable_channels = [1473501780125028393, 1389065576953024603]
        if message.channel.id in acceptable_channels and "kiwi" in message.content.lower():
            response = llm.get_llm_response(role="user", name=str(message.author.global_name), user_id=message.author.id, user_input=message.content)
            await message.channel.send(response)


    @bot.event
    async def on_error(event: str, *args: tuple[object, ...]) -> None:
        logger.error(f"Unhandled exception in event {event}: {args}")
        traceback.print_exc()


def add_slash_commands_to_tree(tree: app_commands.CommandTree) -> None:
    print("Slash commands not implemented.")


def add_prefix_commands_to_bot(bot: commands.Bot) -> None:
    print("Prefix commands not implemented.")


async def setup(bot: commands.Bot) -> None:
    await bot.tree.sync()
    logger.info("Command tree synced globally.")


async def on_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
    logger.error(f"Command error: {error}")
    await interaction.response.send_message(
        embed=create_error_embed(
            "Command error",
            str(error),
        ),
        ephemeral=True,
    )


async def run_bot(bot: commands.Bot) -> None:
    if not TOKEN:
        logger.error("KIWI_DISCORD_TOKEN environment variable not found.")
        raise ValueError("KIWI_DISCORD_TOKEN environment variable not found.")

    logger.info("Starting discord module.")

    try:
        await bot.start(TOKEN)
    except discord.LoginFailure:
        logger.error("Failed to login to discord module.")
        raise
    except Exception as e:
        logger.error("Unexpected error during discord module loading.")
        raise


async def main() -> None:
    bot: commands.Bot = create_bot()
    register_events(bot)
    add_slash_commands_to_tree(bot.tree)
    add_prefix_commands_to_bot(bot)
    async def setup_hook() -> None:
        await setup(bot)
    bot.setup_hook = setup_hook
    bot.tree.error(on_command_error)
    await run_bot(bot)


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
