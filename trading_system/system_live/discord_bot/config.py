# discord_trade_bot/config.py
from __future__ import annotations

from dataclasses import dataclass
import os

from dotenv import load_dotenv

# Load .env into environment
load_dotenv()


@dataclass
class BotSettings:
    """Configuration for the Discord trading bot."""
    token: str
    guild_id: int
    channel_id: int
    trader_user_id: int

    @classmethod
    def from_env(cls) -> "BotSettings":
        try:
            token = os.environ["DISCORD_BOT_TOKEN"]
        except KeyError as exc:
            raise RuntimeError(
                "DISCORD_BOT_TOKEN is not set in .env"
            ) from exc

        try:
            guild_id = int(os.environ["DISCORD_GUILD_ID"])
            channel_id = int(os.environ["DISCORD_CHANNEL_ID"])
            trader_user_id = int(os.environ["DISCORD_TRADER_USER_ID"])
        except KeyError as exc:
            raise RuntimeError(
                "DISCORD_GUILD_ID, DISCORD_CHANNEL_ID, and DISCORD_TRADER_USER_ID "
                "must be set in .env"
            ) from exc

        return cls(
            token=token,
            guild_id=guild_id,
            channel_id=channel_id,
            trader_user_id=trader_user_id,
        )