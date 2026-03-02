from aiogram import BaseMiddleware
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from typing import Callable, Dict, Any, Awaitable

class AuthMiddleware(BaseMiddleware):
    """
    Middleware that ensures users are authenticated before allowing access
    to certain handlers. It checks for a valid access token in the FSM context.
    """
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        state: FSMContext = data.get("state")
        if not state:
            return await handler(event, data)

        # Allow Web App data (login response) to pass through
        if event.web_app_data:
             return await handler(event, data)

        current_state = await state.get_state()
        
        # Allow login flow and start command without auth
        if current_state in ["LoginStates:waiting_for_username", "LoginStates:waiting_for_password"] or \
           (event.text and event.text.startswith(("/start", "/login"))):
            return await handler(event, data)

        user_data = await state.get_data()
        token = user_data.get("access_token")

        if not token:
            await event.answer("⚠️ You are not logged in. Please use /login to authenticate.")
            return

        # Pass token to handler via data if needed, or just rely on state
        data["access_token"] = token
        return await handler(event, data)