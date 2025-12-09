# run_trade_bot.py

# --- BEGIN: workaround for missing _zstd on Pi ---
import sys
import types

# Create a dummy _zstd module so imports don't fail.
# We don't actually use zstandard compression anywhere in this bot.
if "_zstd" not in sys.modules:
    sys.modules["_zstd"] = types.ModuleType("_zstd")
# --- END: workaround for missing _zstd on Pi ---

from system.system_live.discord_bot.bot_core import main

if __name__ == "__main__":
    main()