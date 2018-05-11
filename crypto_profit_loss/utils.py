from .models import User, BinanceAcct
from .schemas import UserSchema, AccountSchema
from .database import scoped
from binance.client import Client

US = UserSchema()
AS = AccountSchema()


# TODO
# want to get all trades
# then get the USDT value of assets at time of trade
# want to compare current USDT value to value at the time
# want to compare current value to value paid in underlying


def update_user(user_id: int):
    with scoped() as s:
        user: User = s.query(User).get(user_id)
        if not user:
            raise KeyError(f'no such user {user_id}')
        client: Client = Client(user.api_key, user.api_secret)
        acct: dict = client.get_account()
        # TODO error checking here
        acct_sql: BinanceAcct = AS.load(acct).data
        acct_cached: BinanceAcct = user.account
        if acct_cached:
            for k in acct.keys():
                if k != 'balances':
                    setattr(acct_cached, k, getattr(acct_sql, k))
        else:
            s.add(acct_sql)
        # TODO generic_commit?
        try:
            s.commit()
        except Exception as e:
            print(e)


def get_specific_user_acct_status(user_id):
    with scoped() as s:
        user = s.query(User).get(user_id)
        client = Client(user.api_key, user.api_secret)
        return client.get_account_status()


def update_all_trades():
    ...


def underlying_to_usdt_at_time(underlying_instrument, time):
    ...


def get_profit_loss(trade):
    instrument = trade.pair[:3]
    underlying = trade.pair[3:]
    ...
