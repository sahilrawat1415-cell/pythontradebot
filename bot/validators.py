"""
Input validators for trading bot parameters.

Validates symbol, side, order type, quantity, and price
before they reach the API layer.
"""

import logging
from typing import Optional

logger = logging.getLogger("trading_bot")

# ── Constants ────────────────────────────────────────────────────────────────

VALID_SIDES = ("BUY", "SELL")
VALID_ORDER_TYPES = ("MARKET", "LIMIT", "STOP_MARKET")

# Common Binance Futures USDT-M symbols (non-exhaustive, API will reject invalid ones)
EXAMPLE_SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "XRPUSDT", "DOGEUSDT",
    "SOLUSDT", "ADAUSDT", "AVAXUSDT", "DOTUSDT", "MATICUSDT",
]


class ValidationError(Exception):
    """Raised when user input fails validation."""
    pass


def validate_symbol(symbol: str) -> str:
    """
    Validate and normalize the trading symbol.

    Args:
        symbol: Trading pair symbol (e.g., 'btcusdt').

    Returns:
        Uppercased symbol string.

    Raises:
        ValidationError: If symbol is empty or contains invalid characters.
    """
    if not symbol or not symbol.strip():
        raise ValidationError("Symbol cannot be empty.")

    symbol = symbol.strip().upper()

    if not symbol.isalpha():
        raise ValidationError(
            f"Invalid symbol '{symbol}'. Symbol must contain only letters (e.g., BTCUSDT)."
        )

    if len(symbol) < 5:
        raise ValidationError(
            f"Invalid symbol '{symbol}'. Symbol seems too short (e.g., BTCUSDT)."
        )

    if not symbol.endswith("USDT"):
        logger.warning(
            "Symbol '%s' does not end with USDT. "
            "This bot targets USDT-M futures — ensure symbol is correct.",
            symbol,
        )

    logger.debug("Symbol validated: %s", symbol)
    return symbol


def validate_side(side: str) -> str:
    """
    Validate the order side.

    Args:
        side: Order side ('BUY' or 'SELL').

    Returns:
        Uppercased side string.

    Raises:
        ValidationError: If side is not BUY or SELL.
    """
    if not side or not side.strip():
        raise ValidationError("Side cannot be empty.")

    side = side.strip().upper()

    if side not in VALID_SIDES:
        raise ValidationError(
            f"Invalid side '{side}'. Must be one of: {', '.join(VALID_SIDES)}"
        )

    logger.debug("Side validated: %s", side)
    return side


def validate_order_type(order_type: str) -> str:
    """
    Validate the order type.

    Args:
        order_type: Order type ('MARKET', 'LIMIT', or 'STOP_MARKET').

    Returns:
        Uppercased order type string.

    Raises:
        ValidationError: If order type is not supported.
    """
    if not order_type or not order_type.strip():
        raise ValidationError("Order type cannot be empty.")

    order_type = order_type.strip().upper()

    if order_type not in VALID_ORDER_TYPES:
        raise ValidationError(
            f"Invalid order type '{order_type}'. "
            f"Must be one of: {', '.join(VALID_ORDER_TYPES)}"
        )

    logger.debug("Order type validated: %s", order_type)
    return order_type


def validate_quantity(quantity: str) -> float:
    """
    Validate order quantity.

    Args:
        quantity: Order quantity as string.

    Returns:
        Validated quantity as float.

    Raises:
        ValidationError: If quantity is not a positive number.
    """
    try:
        qty = float(quantity)
    except (ValueError, TypeError):
        raise ValidationError(
            f"Invalid quantity '{quantity}'. Must be a positive number."
        )

    if qty <= 0:
        raise ValidationError(
            f"Invalid quantity '{qty}'. Must be greater than zero."
        )

    logger.debug("Quantity validated: %s", qty)
    return qty


def validate_price(price: Optional[str], order_type: str) -> Optional[float]:
    """
    Validate order price. Required for LIMIT and STOP_MARKET orders.

    Args:
        price: Order price as string (can be None for MARKET orders).
        order_type: The order type to determine if price is required.

    Returns:
        Validated price as float, or None for MARKET orders.

    Raises:
        ValidationError: If price is missing when required or is invalid.
    """
    requires_price = order_type in ("LIMIT", "STOP_MARKET")

    if requires_price:
        if price is None or (isinstance(price, str) and not price.strip()):
            raise ValidationError(
                f"Price is required for {order_type} orders."
            )
        try:
            p = float(price)
        except (ValueError, TypeError):
            raise ValidationError(
                f"Invalid price '{price}'. Must be a positive number."
            )
        if p <= 0:
            raise ValidationError(
                f"Invalid price '{p}'. Must be greater than zero."
            )
        logger.debug("Price validated: %s", p)
        return p

    # MARKET orders don't need a price
    if price is not None and str(price).strip():
        logger.warning("Price provided for MARKET order — it will be ignored.")

    return None


def validate_all(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: Optional[str] = None,
) -> dict:
    """
    Validate all order parameters at once.

    Args:
        symbol: Trading pair symbol.
        side: Order side (BUY/SELL).
        order_type: Order type (MARKET/LIMIT/STOP_MARKET).
        quantity: Order quantity.
        price: Order price (required for LIMIT/STOP_MARKET).

    Returns:
        Dictionary with validated parameters.

    Raises:
        ValidationError: If any parameter is invalid.
    """
    validated = {
        "symbol": validate_symbol(symbol),
        "side": validate_side(side),
        "order_type": validate_order_type(order_type),
        "quantity": validate_quantity(quantity),
        "price": validate_price(price, order_type.strip().upper()),
    }

    logger.info("All parameters validated successfully.")
    return validated
