from utils.prices import get_prices
from utils.user_helpers import has_balance, decrement_user_limit, format_balance
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


async def show_price_info(message, user: dict, price_key: str, feature_label: str) -> int:
    """
    Отправить пользователю информацию о цене функции и текущем балансе.

    Returns:
        Стоимость функции.
    """
    prices = await get_prices()
    price = prices.get(price_key, 1)
    balance = format_balance(user)
    await message.answer(f"{feature_label}: будет списано {price} у.е.\n{balance}")
    return price
