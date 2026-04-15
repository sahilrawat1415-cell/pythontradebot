#!/usr/bin/env python3
"""
CLI entry point for the Binance Futures Testnet Trading Bot.

Provides two interfaces:
  1. Direct command-line mode (via arguments)
  2. Interactive menu mode (via --interactive flag)

Usage examples:
  python cli.py order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
  python cli.py order --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.01 --price 3500
  python cli.py --interactive
"""

import os
import sys
from typing import Optional

import click
from dotenv import load_dotenv

from bot.client import BinanceClient, BinanceAPIError
from bot.logging_config import setup_logging
from bot.orders import place_order
from bot.validators import validate_all, ValidationError, VALID_SIDES, VALID_ORDER_TYPES

# ── Initialisation ───────────────────────────────────────────────────────────

load_dotenv()
logger = setup_logging()


def _get_client() -> BinanceClient:
    """
    Create and return a BinanceClient using environment variables.

    Raises:
        click.ClickException: If API credentials are not configured.
    """
    api_key = os.getenv("BINANCE_TESTNET_API_KEY", "")
    api_secret = os.getenv("BINANCE_TESTNET_API_SECRET", "")

    if not api_key or not api_secret or api_key == "your_api_key_here":
        raise click.ClickException(
            "API credentials not configured.\n"
            "  1. Copy .env.example to .env\n"
            "  2. Add your Binance Futures Testnet API key and secret.\n"
            "  3. Get credentials at: https://testnet.binancefuture.com"
        )

    return BinanceClient(api_key, api_secret)


# ── Interactive Mode ─────────────────────────────────────────────────────────

def _print_banner():
    """Print the application banner."""
    banner = """
+=================================================================+
|                                                                 |
|        BINANCE FUTURES TESTNET TRADING BOT                      |
|                                                                 |
|        Place orders on Binance Futures Testnet (USDT-M)         |
|        Supported: MARKET | LIMIT | STOP_MARKET                  |
|                                                                 |
+=================================================================+
"""
    click.echo(click.style(banner, fg="cyan", bold=True))


def _interactive_menu():
    """Run the interactive menu for order placement."""
    _print_banner()

    client = _get_client()

    while True:
        click.echo(click.style("\n── Main Menu ──", fg="yellow", bold=True))
        click.echo("  [1] Place an Order")
        click.echo("  [2] Place a Quick MARKET BUY")
        click.echo("  [3] Place a Quick MARKET SELL")
        click.echo("  [0] Exit")
        click.echo()

        choice = click.prompt(
            click.style("Select an option", fg="green"),
            type=click.IntRange(0, 3),
        )

        if choice == 0:
            click.echo(click.style("\nGoodbye!\n", fg="cyan"))
            break

        elif choice == 1:
            _interactive_place_order(client)

        elif choice == 2:
            _interactive_quick_market(client, "BUY")

        elif choice == 3:
            _interactive_quick_market(client, "SELL")


def _interactive_place_order(client: BinanceClient):
    """Prompt the user for all order parameters and place the order."""
    click.echo(click.style("\n── Place Order ──\n", fg="yellow", bold=True))

    symbol = click.prompt("  Symbol (e.g., BTCUSDT)", type=str)
    side = click.prompt(
        "  Side",
        type=click.Choice(VALID_SIDES, case_sensitive=False),
    )
    order_type = click.prompt(
        "  Order Type",
        type=click.Choice(VALID_ORDER_TYPES, case_sensitive=False),
    )
    quantity = click.prompt("  Quantity", type=str)

    price = None
    if order_type.upper() in ("LIMIT", "STOP_MARKET"):
        price_label = "Stop Price" if order_type.upper() == "STOP_MARKET" else "Price"
        price = click.prompt(f"  {price_label}", type=str)

    _execute_order(client, symbol, side, order_type, quantity, price)


def _interactive_quick_market(client: BinanceClient, side: str):
    """Prompt for symbol and quantity, then place a MARKET order."""
    click.echo(
        click.style(
            f"\n── Quick MARKET {side} ──\n", fg="yellow", bold=True
        )
    )

    symbol = click.prompt("  Symbol (e.g., BTCUSDT)", type=str)
    quantity = click.prompt("  Quantity", type=str)

    _execute_order(client, symbol, side, "MARKET", quantity, None)


# ── Order Execution ──────────────────────────────────────────────────────────

def _execute_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: Optional[str],
):
    """
    Validate inputs and execute an order, handling all errors gracefully.

    Args:
        client: Initialised BinanceClient.
        symbol: Trading pair symbol.
        side: BUY or SELL.
        order_type: MARKET, LIMIT, or STOP_MARKET.
        quantity: Order quantity (string, will be validated).
        price: Order price (string or None).
    """
    try:
        # Validate all inputs
        validated = validate_all(symbol, side, order_type, quantity, price)

        # Place the order
        place_order(
            client=client,
            symbol=validated["symbol"],
            side=validated["side"],
            order_type=validated["order_type"],
            quantity=validated["quantity"],
            price=validated["price"],
        )

    except ValidationError as e:
        logger.error("[FAIL] Validation error: %s", e)
        click.echo(click.style(f"\n[FAIL] Validation Error: {e}\n", fg="red"))

    except BinanceAPIError as e:
        logger.error("[FAIL] Binance API error: %s", e)
        click.echo(click.style(f"\n[FAIL] API Error: {e}\n", fg="red"))

    except Exception as e:
        logger.exception("[FAIL] Unexpected error during order placement")
        click.echo(
            click.style(f"\n[FAIL] Unexpected Error: {e}\n", fg="red")
        )


# ── Click CLI ────────────────────────────────────────────────────────────────

@click.group(invoke_without_command=True)
@click.option(
    "--interactive", "-i",
    is_flag=True,
    help="Launch interactive menu mode.",
)
@click.pass_context
def cli(ctx, interactive):
    """
    Binance Futures Testnet Trading Bot

    Place MARKET, LIMIT, and STOP_MARKET orders on Binance Futures
    Testnet (USDT-M) via CLI or interactive mode.
    """
    if interactive:
        _interactive_menu()
    elif ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command()
@click.option(
    "--symbol", "-s",
    required=True,
    help="Trading pair symbol (e.g., BTCUSDT).",
)
@click.option(
    "--side",
    required=True,
    type=click.Choice(["BUY", "SELL"], case_sensitive=False),
    help="Order side: BUY or SELL.",
)
@click.option(
    "--type", "order_type",
    required=True,
    type=click.Choice(["MARKET", "LIMIT", "STOP_MARKET"], case_sensitive=False),
    help="Order type: MARKET, LIMIT, or STOP_MARKET.",
)
@click.option(
    "--quantity", "-q",
    required=True,
    help="Order quantity.",
)
@click.option(
    "--price", "-p",
    default=None,
    help="Order price (required for LIMIT and STOP_MARKET orders).",
)
def order(symbol, side, order_type, quantity, price):
    """Place an order on Binance Futures Testnet."""
    _print_banner()
    client = _get_client()
    _execute_order(client, symbol, side, order_type, quantity, price)


# ── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    cli()
