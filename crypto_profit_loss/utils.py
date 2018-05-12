import binance
from binance.client import Client
from marshmallow.exceptions import ValidationError
from .models.user import User, BinanceAcct
from .schemas import UserSchema, AccountSchema, BalanceSchema
from .database import scoped

US = UserSchema()
AS = AccountSchema()
BS = BalanceSchema()

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
        acct_id = None
        if acct_cached:
            for k in acct.keys():
                if k != 'balances':
                    setattr(acct_cached, k, getattr(acct_sql, k))
            cached_balances = acct_cached.make_balance_dict()
            acct_id = acct_cached.id
        else:
            acct_sql.user_id = user_id
            s.add(acct_sql)
            s.flush()
            cached_balances = {}
            acct_id = acct_sql.id
        s.flush()
        for balance in acct['balances']:
            try:
                parsed_balance = BS.load(balance).data
            except ValidationError as e:
                print(e)
                raise
            bal = cached_balances.get(parsed_balance.asset)
            if not bal:
                parsed_balance.account_id = acct_id
                s.add(parsed_balance)
            else:
                # these changes should be picked up and be on the session
                for k in balance.keys():
                    setattr(bal, k, getattr(parsed_balance, k))
        # TODO generic_commit?
        try:
            s.commit()
        except Exception as e:
            print(e)
        return


def get_specific_user_acct_status(user_id: int):
    with scoped() as s:
        user: User = s.query(User).get(user_id)
        client = Client(user.api_key, user.api_secret)
        return client.get_account_status()


def update_all_trades(user_id, pair):
    with scoped() as s:
        user: User = s.query(User).get(user_id)
        if not user:
            raise KeyError('no such user')
        if not user.account:
            update_user(user_id)
            user: User = s.query(User).get(user_id)
        client = Client(user.api_key, user.api_secret)
        trades = client.get_my_trades(symbol=pair, fromId=user.account.last_trade)
        TS = TradeSchema()
        for trade in trades:
            if s.query(Trade).get(trade['id']):
                # trade already exists in the database
                continue
            try:
                parsed_trade = TS.load(trade)
            except ValidationError as e:
                print(e)
            parsed_trade.account_id = user.account.id
            s.add(parsed_trade)
        # update the most recent trade parsed for the account
        user.account.last_trade = parsed_trade.id
        return



def underlying_to_usdt_at_time(underlying_instrument, time):
    """
    So we should have the USDT value for things traded against USDT. Everythine
    """
    client = Client('', '')
    interval = interval_to_milliseconds(Client.KLINE_INTERVAL_1MINUTE)
    data = client.get_klines(symbol=underlying_instrument, interval=interval, limit=500, startTime=time,
                             endTime=time+60000)
    print(data)

def get_profit_loss(trade):
    instrument = trade.pair[:3]
    underlying = trade.pair[3:]
    ...

# Thanks to samchardy.github.io for this ftn
def interval_to_milliseconds(interval):
    """Convert a Binance interval string to milliseconds
    :param interval: Binance interval string 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w
    :type interval: str
    :return:
         None if unit not one of m, h, d or w
         None if string not in correct format
         int value of interval in milliseconds
    """
    ms = None
    seconds_per_unit = {
        "m": 60,
        "h": 60 * 60,
        "d": 24 * 60 * 60,
        "w": 7 * 24 * 60 * 60
    }

    unit = interval[-1]
    if unit in seconds_per_unit:
        try:
            ms = int(interval[:-1]) * seconds_per_unit[unit] * 1000
        except ValueError:
            pass
    return ms
