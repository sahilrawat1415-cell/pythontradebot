"""
Order placement logic for Binance Futures Testnet.

Builds order parameters and delegates execution to the BinanceClient.
Supports MARKET, LIMIT, and STOP_MARKET order types.
"""

import logging
from typing import Any, Dict, Optional

from bot.client import BinanceClient

logger = logging.getLogger("trading_bot")


def _build_order_params(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Build the parameter dictionary for an order request.

    Args:
        symbol: Trading pair (e.g., 'BTCUSDT').
        side: 'BUY' or 'SELL'.
        order_type: 'MARKET', 'LIMIT', or 'STOP_MARKET'.
        quantity: Order quantity.
        price: Order price (required for LIMIT; used as stopPrice for STOP_MARKET).

    Returns:
        Dictionary of order parameters ready for the API.
    """
    params: Dict[str, Any] = {
        "symbol": symbol,
        "side": side,
        "type": order_type,
        "quantity": quantity,
    }

    if order_type == "LIMIT":
        params["price"] = price
        params["timeInForce"] = "GTC"  # Good Till Cancelled

    elif order_type == "STOP_MARKET":
        params["stopPrice"] = price
        params["closePosition"] = "false"

    logger.debug("Order params built: %s", params)
    return params


def _format_order_summary(params: Dict[str, Any]) -> str:
    """
    Format a human-readable order request summary.

    Args:
        params: Order parameters dictionary.

    Returns:
        Formatted summary string.
    """
    lines = [
        "",
        "+----------------------------------------------+",
        "|            ORDER REQUEST SUMMARY              |",
        "+----------------------------------------------+",
        f"|  Symbol     : {params['symbol']:<30} |",
        f"|  Side       : {params['side']:<30} |",
        f"|  Type       : {params['type']:<30} |",
        f"|  Quantity   : {str(params['quantity']):<30} |",
    ]

    if "price" in params:
        lines.append(f"|  Price      : {str(params['price']):<30} |")
    if "stopPrice" in params:
        lines.append(f"|  Stop Price : {str(params['stopPrice']):<30} |")
    if "timeInForce" in params:
        lines.append(f"|  TIF        : {params['timeInForce']:<30} |")

    lines.append("+----------------------------------------------+")
    lines.append("")

    return "\n".join(lines)


def _format_order_response(response: Dict[str, Any]) -> str:
    """
    Format a human-readable order response summary.

    Args:
        response: API order response dictionary.

    Returns:
        Formatted response string.
    """
    order_id = response.get("orderId", "N/A")
    status = response.get("status", "N/A")
    executed_qty = response.get("executedQty", "N/A")
    avg_price = response.get("avgPrice", "N/A")
    client_order_id = response.get("clientOrderId", "N/A")
    order_type = response.get("type", "N/A")
    side = response.get("side", "N/A")
    symbol = response.get("symbol", "N/A")
    orig_qty = response.get("origQty", "N/A")

    lines = [
        "",
        "+----------------------------------------------+",
        "|           ORDER RESPONSE DETAILS              |",
        "+----------------------------------------------+",
        f"|  Order ID      : {str(order_id):<27} |",
        f"|  Client OID    : {str(client_order_id):<27} |",
        f"|  Symbol        : {str(symbol):<27} |",
        f"|  Side          : {str(side):<27} |",
        f"|  Type          : {str(order_type):<27} |",
        f"|  Status        : {str(status):<27} |",
        f"|  Orig Qty      : {str(orig_qty):<27} |",
        f"|  Executed Qty  : {str(executed_qty):<27} |",
        f"|  Avg Price     : {str(avg_price):<27} |",
        "+----------------------------------------------+",
        "",
    ]

    return "\n".join(lines)


def place_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Place an order on Binance Futures Testnet.

    Builds order parameters, logs the request summary, sends the order
    via the client, and logs the response.

    Args:
        client: Initialised BinanceClient instance.
        symbol: Trading pair (e.g., 'BTCUSDT').
        side: 'BUY' or 'SELL'.
        order_type: 'MARKET', 'LIMIT', or 'STOP_MARKET'.
        quantity: Order quantity.
        price: Order price (required for LIMIT/STOP_MARKET).

    Returns:
        API response dictionary with order details.
    """
    # Build params
    params = _build_order_params(symbol, side, order_type, quantity, price)

    # Print & log the request summary
    summary = _format_order_summary(params)
    logger.info(summary)

    # Send order
    response = client.place_order(params)

    # Print & log the response
    resp_summary = _format_order_response(response)
    logger.info(resp_summary)

    # Success message
    status = response.get("status", "UNKNOWN")
    order_id = response.get("orderId", "N/A")

    if status in ("NEW", "FILLED", "PARTIALLY_FILLED"):
        logger.info(
            "[OK] Order placed successfully! Order ID: %s | Status: %s",
            order_id,
            status,
        )
    else:
        logger.warning(
            "[WARN] Order placed with status: %s | Order ID: %s",
            status,
            order_id,
        )

    return response
