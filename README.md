# MoneyCounter

MoneyCounter is a smart, AI-powered personal finance tracking application. The platform leverages a Django-based REST API backend integrated with AI microservices (Whisper for voice-to-text, Ollama for LLM-based parsing) and an Aiogram-based Telegram Bot frontend.

## 🌟 Key Features

* **Voice & Text Input:** Send a quick text like "Dinner 1200" or a voice message like "Spent 500 on groceries." The system automatically transcribes and categorizes your transaction using AI.
* **Smart Categorization:** Uses an LLM (Language Model via LangChain + Ollama) to parse natural language inputs into structured transaction data, mapping them to your personalized categories.
* **Multi-Account Support:** Track balances across multiple accounts and easily perform transfers between them.
* **Telegram Mini App Integration:** Seamless registration and login directly within Telegram using the Telegram WebApp platform.
* **Analytics & Reporting:** View your income, expenses, and net cash flow directly inside the bot with weekly or monthly summaries.
* **Asynchronous Processing:** Voice parsing and LLM invocations are handled as background tasks by Celery and Redis, ensuring the bot remains snappy.

---

## 🏗️ Architecture

The project is divided into several main components:

### 1. Backend (`moneycounter/`)

Built with **Django** and **Django REST Framework (DRF)**.

* **`finance/`**: Manages the core business logic—Accounts, Categories, Transactions, Subscriptions, and Financial Goals. Includes analytical views and API endpoints.
* **`user_auth/`**: Custom user model with base currency preferences and JWT authentication endpoints.
* **`ai_services/`**:
  * **LLM Service**: Connects to a local Ollama instance (default `qwen2.5:3b`) using Langchain to extract amounts, categories, and descriptions from natural text.
  * **STT Service**: Connects to a Whisper API to transcribe `.ogg` voice notes sent via Telegram.
  * **Tasks**: Celery tasks (`process_voice_transaction_task`, `process_text_transaction_task`) to perform heavy AI workloads without blocking the main API.

### 2. Telegram Bot (`telegram_bot/`)

Built with **Aiogram 3**.

* Acts as the primary user interface.
* Uses **FSM (Finite State Machine)** backed by Redis for complex conversational flows (e.g., editing transactions, adding accounts, transferring money).
* Consumes the Django REST API through dedicated service classes (`services/`).
* Uses **Auth Middleware** to securely inject access tokens to authorized users.

---

## 🚀 Getting Started

### Prerequisites

* Python 3.10+
* Redis (for Celery broker & Aiogram FSM)
* [Ollama](https://ollama.ai/) running locally with the `qwen2.5:3b` model (or configure a different model).
* A running [Whisper ASR web service](https://github.com/ahmetzan/whisper-asr-webservice) (or similar).

### 1. Environment Variables

Create a `.env` file in the root directory (refer to `.env.example` if available). Example:

```env
# Bot Setup
BOT_TOKEN=your_telegram_bot_token
API_BASE_URL=http://localhost:8000
WEBAPP_URL=https://your-ngrok-url.ngrok.io  # Important for Telegram Mini App

# Django Setup
SECRET_KEY=your_django_secret
DEBUG=True
```

### 2. Backend Setup

```bash
cd moneycounter
# Install dependencies (assuming a shared venv or pip install -r requirements.txt)
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Create a superuser
python manage.py createsuperuser

# Run the Django dev server
python manage.py runserver
```

### 3. Celery Worker Setup

In a new terminal window:

```bash
cd moneycounter
# Run Celery worker to process AI tasks
celery -A moneycounter worker -l info
```

### 4. Telegram Bot Setup

In another terminal window:

```bash
cd telegram_bot
# Install dependencies if not already done
pip install -r requirements.txt

# Run the bot
python bot.py
```

---

## 🛠️ Tech Stack

* **Backend API**: Python, Django, Django REST Framework, SimpleJWT.
* **Background Tasks**: Celery, Redis.
* **AI Integration**: LangChain, Ollama (`qwen2.5:3b`), Whisper API.
* **Bot Frontend**: Python, Aiogram 3.x, Telegram WebApp.
* **String Matching**: `thefuzz` (for mapping LLM category outputs strictly to DB categories).

---

## 📋 TODO / Future Improvements

* [ ] **Recalculate all transactions into base currency**: Now its just gives you sum of all your transactions and if u add transactions in different currencies it will just calculate it as is.
* [ ] **Every n-time currency exchange rate update**: Use API to get current currency rate and save it in database. Probably need to use celery task to do it once a while.
* [ ] **AI Advice / Goals**: "Can I afford to buy this?" logic using the LLM based on user balances and goals.
* [ ] **Detailed Analytics**: Send dynamically generated charts and PDF reports straight to Telegram.
* [ ] **Subscription Reminders**: Celery periodic tasks to warn about upcoming payments.
* [ ] **Dockerization**: Complete `docker-compose.yml` to spin up Django, Redis, Bot, Ollama, and Whisper together easily.
