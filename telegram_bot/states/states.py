from aiogram.fsm.state import State, StatesGroup

class LoginStates(StatesGroup):
    """States for the user login flow."""
    waiting_for_username = State()
    waiting_for_password = State()

class TransactionStates(StatesGroup):
    """States for transaction creation and confirmation."""
    waiting_for_confirmation = State()
    waiting_for_category = State()

class EditStates(StatesGroup):
    """States for editing an existing transaction."""
    selecting_field = State()
    waiting_for_amount = State()
    waiting_for_category = State()
    waiting_for_description = State()

class FilterCategoryStates(StatesGroup):
    """States for filtering transactions by category."""
    selecting_category = State()

class FilterPeriodStates(StatesGroup):
    """States for filtering transactions by a specific time period."""
    waiting_for_start_date = State()
    waiting_for_end_date = State()

class AddAccountStates(StatesGroup):
    """States for creating a new financial account."""
    waiting_for_name = State()
    waiting_for_currency = State()
    waiting_for_balance = State()

class EditAccountStates(StatesGroup):
    """States for editing an existing financial account."""
    selecting_field = State()
    waiting_for_name = State()
    waiting_for_balance = State()

class TransferStates(StatesGroup):
    """States for transferring money between accounts."""
    selecting_source = State()
    selecting_destination = State()
    waiting_for_amount = State()

class SettingsStates(StatesGroup):
    """States for configuring user settings (e.g. changing base currency)."""
    selecting_currency = State()

class CategorySettingsStates(StatesGroup):
    """States for managing and editing transaction categories."""
    waiting_for_name = State()
    waiting_for_type = State()
    waiting_for_essential = State()
    # Edit mode
    selecting_edit_field = State()
    editing_name = State()
    editing_type = State()
    editing_essential = State()
