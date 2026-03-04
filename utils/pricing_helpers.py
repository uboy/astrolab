from utils.prices import get_prices
from utils.user_helpers import has_balance, decrement_user_limit
from utils.constants import MSG_NOT_ENOUGH_FUNDS


async def ensure_balance_and_charge(message, price_key: str, user, feature: str, details=None):
    prices = await get_prices()
    price = prices.get(price_key, 1)
    if not has_balance(user, price):
        await message.answer(MSG_NOT_ENOUGH_FUNDS.format(feature=feature, price=price, free=user["free_count"], paid=user["paid_count"]))
        return None
    user = await decrement_user_limit(
        message.from_user.id,
        price=price,
        feature=feature,
        details=details or {},
        telegram_user=message.from_user
    )
    return user
