# discord_trade_bot/bot_core.py
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Literal, Dict, Any

import discord
from discord.ext import commands

from .config import BotSettings

log = logging.getLogger(__name__)


@dataclass
class TradeCandidate:
    """Simple example of a trade to send to Discord."""
    symbol: str
    direction: Literal["LONG", "SHORT"]
    size: float
    entry_price: float
    stop_loss: float
    take_profit: float
    r_multiple: float
    notes: str | None = None

    def to_embed(self) -> discord.Embed:
        """Render the trade as a Discord embed."""
        colour = discord.Colour.green() if self.direction == "LONG" else discord.Colour.red()
        desc = self.notes or "Sample trade generated from the Pi."

        embed = discord.Embed(
            title=f"Trade candidate: {self.symbol} ({self.direction})",
            description=desc,
            colour=colour,
        )
        embed.add_field(name="Size", value=str(self.size), inline=True)
        embed.add_field(name="Entry", value=str(self.entry_price), inline=True)
        embed.add_field(name="Stop Loss", value=str(self.stop_loss), inline=True)
        embed.add_field(name="Take Profit", value=str(self.take_profit), inline=True)
        embed.add_field(name="R-multiple", value=str(self.r_multiple), inline=True)

        return embed


class TradeBot(commands.Bot):
    """Discord bot that can ask for confirmation on trades."""

    def __init__(self, settings: BotSettings):
        self.settings = settings

        intents = discord.Intents.default()
        intents.message_content = True  # needed if we want to read your typed replies

        super().__init__(
            command_prefix="!",
            intents=intents,
        )

    async def setup_hook(self) -> None:
        """Called when the bot is starting up."""
        # Register a simple /ping command for sanity
        @self.tree.command(name="ping", description="Check that the bot is alive.")
        async def ping(interaction: discord.Interaction):
            await interaction.response.send_message("Pong! 🏓", ephemeral=True)

        # Sync commands just to your guild so they show up quickly
        guild = discord.Object(id=self.settings.guild_id)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)
        log.info("Synced slash commands to guild %s", self.settings.guild_id)

        # Start a demo flow once the bot is ready
        self.loop.create_task(self.demo_trade_flow())

    async def on_ready(self) -> None:
        log.info("Logged in as %s (ID: %s)", self.user, self.user.id)

    # ------------------------------------------------------------------ #
    # Core interaction: send trade, add reactions, wait for your input   #
    # ------------------------------------------------------------------ #

    async def ask_trade_confirmation(
        self,
        trade: TradeCandidate,
        timeout_reaction: float = 300.0,
        timeout_comment: float = 300.0,
    ) -> Dict[str, Any]:
        """
        Send a trade to Discord, add 3 reactions, wait for your choice, and
        optionally your comment. Returns a dict with the decision.
        """
        channel = self.get_channel(self.settings.channel_id)
        if channel is None:
            raise RuntimeError(
                f"Could not find channel with ID {self.settings.channel_id}. "
                "Check DISCORD_CHANNEL_ID."
            )

        embed = trade.to_embed()
        embed.set_footer(text="React to confirm / reject / comment.")

        # Send the message
        message = await channel.send(embed=embed)

        # Add the three reactions from the bot
        reactions = {
            "✅": "CONFIRM",
            "❌": "REJECT",
            "✏️": "COMMENT",
        }
        for emoji in reactions.keys():
            await message.add_reaction(emoji)

        # Wait for YOUR reaction
        def reaction_check(reaction: discord.Reaction, user: discord.User | discord.Member) -> bool:
            return (
                user.id == self.settings.trader_user_id
                and reaction.message.id == message.id
                and str(reaction.emoji) in reactions
            )

        try:
            reaction, user = await self.wait_for(
                "reaction_add",
                timeout=timeout_reaction,
                check=reaction_check,
            )
        except asyncio.TimeoutError:
            log.warning("Timeout waiting for reaction.")
            return {
                "decision": "NO_RESPONSE",
                "comment": None,
                "emoji": None,
            }

        decision = reactions[str(reaction.emoji)]
        comment: str | None = None

        # If you chose "comment", prompt you for a message
        if decision == "COMMENT":
            prompt = await channel.send(
                f"{user.mention} you chose ✏️. Please type your comment for this trade."
            )

            def message_check(msg: discord.Message) -> bool:
                return (
                    msg.author.id == self.settings.trader_user_id
                    and msg.channel.id == channel.id
                )

            try:
                reply: discord.Message = await self.wait_for(
                    "message",
                    timeout=timeout_comment,
                    check=message_check,
                )
            except asyncio.TimeoutError:
                await channel.send("No comment received, timing out.")
                comment = None
            else:
                comment = reply.content
                # Optional: react to your comment to show it was captured
                await reply.add_reaction("✅")
                await channel.send("Comment recorded ✅")

        result = {
            "decision": decision,  # "CONFIRM", "REJECT", "COMMENT"
            "comment": comment,
            "emoji": str(reaction.emoji),
        }

        return result

    # ------------------------------------------------------------------ #
    # Demo flow: send one sample trade & print the result                #
    # ------------------------------------------------------------------ #

    async def demo_trade_flow(self) -> None:
        """
        Fire once at startup: send a sample trade, wait for your response,
        and print it out to the Pi terminal.
        """
        await self.wait_until_ready()  # make sure we're fully connected

        log.info("Starting demo trade flow...")

        trade = TradeCandidate(
            symbol="GBPUSD",
            direction="LONG",
            size=1.0,
            entry_price=1.2500,
            stop_loss=1.2450,
            take_profit=1.2600,
            r_multiple=2.0,
            notes="Sample trade from the Pi v3.",
        )

        try:
            result = await self.ask_trade_confirmation(trade)
        except Exception as e:
            log.exception("Error during demo trade flow: %s", e)
            return

        # This is the bit you wanted: result back in the Python environment
        log.info("Decision from Discord: %s", result)
        print("\n=== Decision from Discord ===")
        print(result)
        print("=== End decision ===\n")


def create_bot() -> TradeBot:
    settings = BotSettings.from_env()
    return TradeBot(settings=settings)


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
    )

    settings = BotSettings.from_env()
    bot = TradeBot(settings=settings)
    bot.run(settings.token)


if __name__ == "__main__":
    main()