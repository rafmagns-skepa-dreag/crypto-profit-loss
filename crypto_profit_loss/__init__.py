from pprint import pprint
from crypto_profit_loss.config import API_KEY, API_SECRET, USER_ID
from crypto_profit_loss.schemas.user import UserSchema
from crypto_profit_loss.database import scoped
from crypto_profit_loss.models.user import User, Balance
from crypto_profit_loss.utils import update_user, update_all_trades
from binance.client import Client


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
        update_user(USER_ID)
        print(s.query(User).all())
        print(len(s.query(Balance).all()))
        update_all_trades(USER_ID, 'XRPETH')
        #client = Client(u.api_key, u.api_secret)
        #pprint(client.get_my_trades(symbol='XRPETH'))
