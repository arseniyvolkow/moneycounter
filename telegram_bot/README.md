# MoneyCounter Telegram Bot

This is a Telegram Bot interface for the MoneyCounter API, designed to help you track expenses via text and voice messages using AI.

## Features

-   **Authentication**: Login with your MoneyCounter credentials.
-   **Voice Transactions**: Send a voice message (e.g., "Bought coffee for 1500") and the AI will transcribe and categorize it.
-   **Text Transactions**: Send a text message (e.g., "Taxi 2000") for quick logging.
-   **Accounts**: View balances of your connected accounts.
-   **Analytics**: (Coming Soon) View spending reports.

## Setup

1.  Navigate to `telegram_bot` directory.
2.  Install requirements:
    ```bash
    pip install -r requirements.txt
    ```
3.  Create a `.env` file (or set environment variables):
    ```env
    BOT_TOKEN=your_telegram_bot_token
    API_BASE_URL=http://localhost:8000
    ```
4.  Run the bot:
    ```bash
    python bot.py
    ```

## Project Status & TODO

Currently implemented:
-   [x] Basic Project Structure (Microservice).
-   [x] Authentication (JWT Middleware).
-   [x] Main Menu & Navigation.
-   [x] Voice to Transaction (Async API integration).
-   [x] Text to Transaction (Async API integration).
-   [x] View Accounts.

To be implemented (Coming Soon):
-   [ ] **Detailed Analytics**: Graphs and PDF reports implementation in `handlers/analytics.py`.
-   [ ] **Transaction Verification**: Interactive confirmation cards (requires API sync mode or polling).
-   [ ] **Goals & Advice**: AI consultation feature ("Can I buy this?").
-   [ ] **Settings**: User preference management.
-   [ ] **Push Notifications**: Morning digests and limit warnings.
