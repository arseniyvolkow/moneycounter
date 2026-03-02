from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from services.analytics import AnalyticsService
from datetime import datetime, timedelta

router = Router()
analytics_service = AnalyticsService()

async def get_report(message: types.Message, state: FSMContext, days: int):
    """
    Fetches and formats an analytics report for the past specified number of days.
    
    Args:
        message (types.Message): The message to reply to.
        state (FSMContext): The FSM context containing the user's token.
        days (int): The number of days to look back for the report.
    """
    data = await state.get_data()
    token = data.get("access_token")
    
    if not token:
        await message.answer("Please login first.")
        return

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    
    report_data = analytics_service.get_analytics(token, start_date=start_str, end_date=end_str)
    
    if report_data is None:
        await message.answer("❌ Failed to fetch analytics.")
        return
        
    expenses = report_data.get('expenses', [])
    income = report_data.get('income', [])
    
    if not expenses and not income:
        await message.answer(f"📭 No data found for the last {days} days.")
        return
        
    # Format report
    title = f"📊 **Report for last {days} days**\n({start_str} - {end_str})\n"
    lines = []
    
    total_expenses = 0
    if expenses:
        lines.append("🔴 **Expenses:**")
        for item in expenses:
            cat_name = item.get('category__name', 'Unknown')
            try:
                total = float(item.get('total', 0))
            except (ValueError, TypeError):
                total = 0.0
                
            if total > 0:
                lines.append(f"• {cat_name}: {total:.2f}")
                total_expenses += total
        lines.append(f"**Total Expenses: {total_expenses:.2f}**")
        lines.append("") # Empty line

    total_income = 0
    if income:
        lines.append("🟢 **Income:**")
        for item in income:
            cat_name = item.get('category__name', 'Unknown')
            try:
                total = float(item.get('total', 0))
            except (ValueError, TypeError):
                total = 0.0
                
            if total > 0:
                lines.append(f"• {cat_name}: {total:.2f}")
                total_income += total
        lines.append(f"**Total Income: {total_income:.2f}**")
        lines.append("")

    net_flow = total_income - total_expenses
    lines.append(f"💰 **Net Flow: {net_flow:+.2f}**")

    text = title + "\n" + "\n".join(lines)
    await message.answer(text, parse_mode="Markdown")

@router.message(F.text == "📅 За неделю")
async def analytics_week(message: types.Message, state: FSMContext):
    """Handles the 'Past Week' analytics request."""
    await get_report(message, state, days=7)

@router.message(F.text == "📅 За месяц")
async def analytics_month(message: types.Message, state: FSMContext):
    """Handles the 'Past Month' analytics request."""
    await get_report(message, state, days=30)

@router.message(F.text == "📉 Сравнение")
async def analytics_compare(message: types.Message):
    """Placeholder handler for the upcoming comparison report."""
    await message.answer("🚧 Comparison report is coming soon!")

@router.message(F.text == "📥 PDF-отчет")
async def analytics_pdf(message: types.Message):
    """Placeholder handler for the upcoming PDF report generation feature."""
    await message.answer("🚧 PDF report generation is coming soon!")
