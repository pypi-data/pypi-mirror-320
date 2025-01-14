import click
import logging
import sys
from . import server

@click.command()
@click.option("--user-id", "-u", required=True, help="The Zoom user ID")
@click.option("--access-token", "-t", required=True, help="The Zoom access token")
@click.option("-v", "--verbose", count=True)
def main(user_id: str, access_token: str, verbose: bool) -> None:
    """MCP Zoom Server - Zoom functionality for MCP"""
    import asyncio

    logging_level = logging.WARN
    if verbose == 1:
        logging_level = logging.INFO
    elif verbose >= 2:
        logging_level = logging.DEBUG

    logging.basicConfig(
        level=logging_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr)

    config = {
        "user_id": user_id,
        "access_token": access_token,
    }

    asyncio.run(server.main(config))

# Optionally expose other important items at package level
__all__ = ["main", "server"]