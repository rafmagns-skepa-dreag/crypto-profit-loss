from crypto_profit_loss.config import API_KEY, API_SECRET, USER_ID
from crypto_profit_loss.schemas.user import UserSchema
from crypto_profit_loss.database import scoped
from crypto_profit_loss.models import User, Balance, Trade
from crypto_profit_loss.utils import update_user, update_all_trades
import asyncio

if __name__ == '__main__':
    with scoped() as s:
        if not s.query(User).all():
            u = User(first_name='Rich', last_name='Hanson', id=USER_ID,
                     api_key=API_KEY,
                     api_secret=API_SECRET)
            s.add(u)
            s.commit()
        else:
            u = s.query(User).get(USER_ID)
        asyncio.get_event_loop().run_until_complete(update_user(USER_ID))
        print(s.query(User).all())
        print(len(s.query(Balance).all()))
        asyncio.get_event_loop().run_until_complete(update_all_trades(USER_ID, 'XRP/ETH'))
        print(len(s.query(Trade).all()))
