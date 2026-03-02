import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from config import BOT_TOKEN
from middleware.auth import AuthMiddleware
from handlers import common, menu, transaction, transaction_history, accounts, settings, analytics

# Configure logging
logging.basicConfig(level=logging.INFO)

async def main():
    """
    Main entry point for the Telegram bot. Initializes the Bot, Dispatcher,
    Redis storage, middleware, and registers all routers before starting polling.
    """
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN is not set!")
        return

    # Initialize Bot and Dispatcher
    bot = Bot(token=BOT_TOKEN)
    
    # Use Redis for FSM storage
    redis = Redis(host="redis", port=6379, db=1)
    storage = RedisStorage(redis=redis)
    
    dp = Dispatcher(storage=storage)

    # Register Middleware
    dp.message.middleware(AuthMiddleware())
    # dp.callback_query.middleware(AuthMiddleware()) # Optional for callbacks

    # Include Routers
    dp.include_router(common.router)
    dp.include_router(menu.router)
    dp.include_router(transaction_history.router)
    dp.include_router(accounts.router)
    dp.include_router(settings.router)
    dp.include_router(analytics.router)
    dp.include_router(transaction.router)

    print("🤖 Bot is starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped!")