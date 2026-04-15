# 🤖 Binance Futures Testnet Trading Bot

A structured Python CLI application for placing **MARKET**, **LIMIT**, and **STOP_MARKET** orders on [Binance Futures Testnet](https://testnet.binancefuture.com) (USDT-M).

---

## 📋 Features

- **Order Types**: MARKET, LIMIT, and STOP_MARKET (bonus)
- **Order Sides**: BUY and SELL
- **Dual CLI Modes**: Direct command-line arguments or interactive menu
- **Input Validation**: Comprehensive validation with clear error messages
- **Structured Logging**: Dual output — console (INFO) + log file (DEBUG)
- **Error Handling**: Handles API errors, network failures, and invalid input
- **Clean Architecture**: Separate client, orders, validators, and CLI layers

---

## 🚀 Setup

### Prerequisites

- Python 3.10+
- A Binance Futures Testnet account

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/trading-bot.git
cd trading-bot
```

### 2. Create a Virtual Environment (recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Credentials

1. Register at [Binance Futures Testnet](https://testnet.binancefuture.com)
2. Generate API Key and Secret from the testnet dashboard
3. Copy the environment template and add your credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```env
BINANCE_TESTNET_API_KEY=your_actual_api_key
BINANCE_TESTNET_API_SECRET=your_actual_api_secret
```

---

## 🎯 How to Run

### Direct CLI Mode

Place orders directly using command-line arguments:

```bash
# MARKET BUY order
python cli.py order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

# MARKET SELL order
python cli.py order --symbol ETHUSDT --side SELL --type MARKET --quantity 0.01

# LIMIT BUY order
python cli.py order --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.001 --price 50000

# LIMIT SELL order
python cli.py order --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.05 --price 4000

# STOP_MARKET order (bonus feature)
python cli.py order --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.001 --price 45000
```

### Interactive Mode

Launch the interactive menu for guided order placement:

```bash
python cli.py --interactive
# or
python cli.py -i
```

### Help

```bash
python cli.py --help
python cli.py order --help
```

---

## 📁 Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py          # Package init with version
│   ├── client.py            # Binance API client (auth, signing, HTTP)
│   ├── orders.py            # Order placement logic & formatting
│   ├── validators.py        # Input validation for all parameters
│   └── logging_config.py    # Dual-handler logging configuration
├── logs/                    # Auto-generated log files
│   ├── trading_bot_market_order.log
│   └── trading_bot_limit_order.log
├── cli.py                   # CLI entry point (Click-based)
├── .env.example             # Environment variable template
├── .gitignore               # Git ignore rules
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

---

## 📝 Output Examples

### Order Request Summary

```
╔══════════════════════════════════════════════╗
║            ORDER REQUEST SUMMARY             ║
╠══════════════════════════════════════════════╣
║  Symbol     : BTCUSDT                        ║
║  Side       : BUY                            ║
║  Type       : MARKET                         ║
║  Quantity   : 0.001                          ║
╚══════════════════════════════════════════════╝
```

### Order Response Details

```
╔══════════════════════════════════════════════╗
║           ORDER RESPONSE DETAILS             ║
╠══════════════════════════════════════════════╣
║  Order ID      : 123456789                   ║
║  Client OID    : abc123def456                ║
║  Symbol        : BTCUSDT                     ║
║  Side          : BUY                         ║
║  Type          : MARKET                      ║
║  Status        : FILLED                      ║
║  Orig Qty      : 0.001                       ║
║  Executed Qty  : 0.001                       ║
║  Avg Price     : 65432.10                    ║
╚══════════════════════════════════════════════╝

✅ Order placed successfully! Order ID: 123456789 | Status: FILLED
```

---

## 🔐 Assumptions

1. **Testnet Only**: This bot connects exclusively to `https://testnet.binancefuture.com`. It does **NOT** interact with the live Binance exchange.
2. **USDT-M Futures**: All orders target USDT-margined futures contracts.
3. **API Credentials**: Stored in a `.env` file (never committed to version control).
4. **Symbol Validation**: Basic format checks are done locally; the Binance API performs the authoritative symbol validation.
5. **Quantity Precision**: The user is responsible for providing quantities that comply with the symbol's lot size filters. The API will reject orders with invalid precision.
6. **Time In Force**: LIMIT orders default to `GTC` (Good Till Cancelled).
7. **STOP_MARKET**: Uses `stopPrice` parameter; does not set `closePosition` by default.
8. **Logging**: Each run creates a new timestamped log file in the `logs/` directory.

---

## 📦 Dependencies

| Package        | Purpose                        |
|----------------|--------------------------------|
| `requests`     | HTTP client for REST API calls |
| `python-dotenv`| Load `.env` configuration      |
| `click`        | CLI framework                  |

---

## 📄 Log Files

Log files are automatically created in the `logs/` directory with timestamps. Each log file captures:

- API request details (endpoint, parameters)
- API response details (status code, body)
- Validation steps
- Errors and exceptions with full tracebacks

Sample log files from test runs are included:
- `logs/trading_bot_market_order.log` — MARKET BUY order
- `logs/trading_bot_limit_order.log` — LIMIT SELL order

---

## ⚡ Bonus Feature

### STOP_MARKET Orders

In addition to MARKET and LIMIT orders, this bot supports **STOP_MARKET** orders:

```bash
python cli.py order --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.001 --price 60000
```

This places a stop-market sell order that triggers when the price drops to 60000 USDT.

### Interactive CLI

The `--interactive` mode provides a guided menu experience with:
- Numbered menu options
- Input prompts with validation
- Quick MARKET order shortcuts
- Color-coded output

---

## 📜 License

This project is provided as-is for demonstration and evaluation purposes.
