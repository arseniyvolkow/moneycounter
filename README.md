# 💰 MoneyCounter

MoneyCounter is a smart, AI-powered personal finance tracking application designed to make expense logging as easy as sending a message. It features a Django REST API backend, AI-driven microservices (Whisper & Ollama), and an interactive Telegram Bot frontend.

## 🌟 Key Features

*   **🗣️ Voice & 📝 Text Input**: Log transactions effortlessly by sending a voice message or a quick text like *"Dinner 1200"* or *"Spent 500 on groceries."*
*   **🤖 AI-Powered Categorization**: Uses a local LLM (**Ollama/Qwen2.5**) to parse natural language, extract amounts, and intelligently map them to categories using **fuzzy string matching**.
*   **💳 Multi-Account & Multi-Currency**: Track balances across multiple accounts (e.g., Cash, Bank, Savings) with support for different currencies.
*   **📊 Smart Analytics**: View instant summaries of your income and expenses for the past week or month directly in Telegram.
*   **🔄 Asynchronous Processing**: Heavy AI workloads (STT and LLM) are handled as background tasks by **Celery & Redis**, ensuring the bot interface remains responsive.
*   **📁 Automatic File Management**: Temporary voice files are automatically processed and cleaned up after transcription.

---

## 🧠 Core Concepts

### AI Parsing Workflow
1.  **Input**: User sends a voice or text message to the Telegram Bot.
2.  **Transcription**: For voice, the **Whisper API** transcribes audio to text.
3.  **Extraction**: The text is sent to a **Qwen2.5:3b** model via **LangChain**. The LLM extracts the `amount`, `currency`, `category`, and `description` in a structured JSON format.
4.  **Refinement**: The extracted category is matched against the user's actual database categories using **Fuzzy Matching** (`thefuzz`) to ensure data integrity.
5.  **Storage**: The transaction is saved, and the user receives a confirmation message.

### Background Tasks
All AI interactions are offloaded to **Celery** workers. This allows the bot to acknowledge your message immediately ("Processing...") while the transcription and parsing happen in the background, notifying you once the transaction is saved.

---

## 🏗️ Architecture

### 1. Backend API (`moneycounter/`)
Powered by **Django** & **DRF**.
*   **`finance/`**: Core logic for Accounts, Transactions, and Categories. Includes models for `Subscriptions` and `FinancialGoal` for future expansion.
*   **`user_auth/`**: Custom user management with JWT authentication and base currency preferences.
*   **`ai_services/`**: Integration layer for Ollama (LLM) and Whisper (STT).

### 2. Telegram Bot (`telegram_bot/`)
Powered by **Aiogram 3**.
*   **State Management**: Uses Redis-backed FSM for secure user sessions.
*   **Hierarchical Menus**: Interactive reply keyboards for navigating between Transactions, Analytics, and Settings.
*   **Service Layer**: Clean separation between bot handlers and API communication.

---

## 🚀 Getting Started

### Quick Start with Docker (Recommended)

The easiest way to run MoneyCounter is using Docker Compose. This spins up the database, Redis, Django API, Celery worker, Telegram bot, and AI services (Ollama and Whisper).

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/MoneyCounter.git
    cd MoneyCounter
    ```

2.  **Environment Variables:**
    ```bash
    cp .env.example .env
    # Edit .env with your BOT_TOKEN and WEBAPP_URL
    ```

3.  **Run with Docker Compose:**
    ```bash
    docker-compose up --build
    ```
    *Note: The first run will download the Whisper model and the Qwen2.5:3b model (approx. 2-4GB).*

---

## 🛠️ Tech Stack

*   **Backend**: Python, Django, DRF, SimpleJWT, Celery, Redis.
*   **AI/LLM**: LangChain, Ollama (`qwen2.5:3b`), OpenAI Whisper.
*   **Bot**: Aiogram 3.x, Pydantic v2.
*   **Database**: PostgreSQL 15, `dj-database-url`.
*   **Utilities**: `thefuzz` (fuzzy matching), `requests`.

---

## 📋 TODO / Future Improvements

*   [ ] **💱 Real-time Currency Conversion**: Implement a Celery periodic task to fetch and update exchange rates for accurate multi-currency totals.
*   [ ] **📅 Recurring Subscriptions**: Expose the existing `Subscriptions` model through the bot for automated recurring expense tracking.
*   [ ] **🎯 Financial Goals**: Fully implement the "Can I afford this?" feature using the `FinancialGoal` model and AI advice.
*   [ ] **📈 Advanced Analytics**: Generate dynamic charts (matplotlib/plotly) and PDF reports.
*   [ ] **🌐 Web Dashboard**: A Next.js or React frontend for more detailed data visualization.
