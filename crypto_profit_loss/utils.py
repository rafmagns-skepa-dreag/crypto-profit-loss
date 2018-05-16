from ccxt.async import binance
from marshmallow.exceptions import ValidationError
from .models import User, BinanceAcct, Trade
from .schemas import UserSchema, AccountSchema, BalanceSchema, TradeSchema
from .database import scoped
from asyncio_extras import async_contextmanager

US = UserSchema()
AS = AccountSchema()
BS = BalanceSchema()

# TODO
# want to get all trades
# then get the USDT value of assets at time of trade
# want to compare current USDT value to value at the time
# want to compare current value to value paid in underlying


async def update_user(user_id: int):
    """
    Fetch a user's account information and balances from Binance and updates it in the database
    :param user_id: ID for the user that will be updated
    :return: None
    """
    with scoped() as s:
        user: User = s.query(User).get(user_id)
        if not user:
            raise KeyError(f'no such user {user_id}')
        async with make_binance(user=user) as exchange:
            try:
                ret = await exchange.fetch_balance()
            except Exception as e:
                raise
        info = ret['info']
        balances = info['balances']
        # # TODO error checking here
        acct_sql: BinanceAcct = AS.load(info).data
        acct_cached: BinanceAcct = user.account
        if acct_cached:
            for k in info.keys():
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
        for balance in acct_sql.balances:
            bal = cached_balances.get(balance.asset)
            if not bal:
                balance.account_id = acct_id
                s.add(balance)
            else:
                # these changes should be picked up and be on the session
                for k in balances[0].keys():
                    setattr(bal, k, getattr(balance, k))
        # TODO generic_commit?
        try:
            s.commit()
        except Exception as e:
            print(e)
        # print(await get_specific_user_acct_status(user_id))

        return


async def get_specific_user_acct_status(user_id: int):
    """
    Fetch the user's account information and balances from Binance
    :param user_id: ID of the user
    :return: dictionary containing user information
    """
    async with make_binance(user_id=user_id) as exchange:
        return await exchange.privateGetAccount()


async def update_trades(user_id, pair):
    """
    Fetches trades for the specified pair for the user and stores them in the database
    :param user_id: ID of the user who's trades are to be updated
    :param pair: currency pair (e.g. 'XRP/ETH') to fetch trades for
    :return:
    """
    with scoped() as s:
        user: User = s.query(User).get(user_id)
        if not user:
            raise KeyError('no such user')
        if not user.account:
            update_user(user_id)
            user: User = s.query(User).get(user_id)

        async with make_binance(user=user) as exchange:
            trades = await exchange.fetch_my_trades(symbol=pair)

        if not trades:
            return

        TS = TradeSchema()
        parsed_trade = None
        for trade in trades:
            if s.query(Trade).get(trade['id']):
                # trade already exists in the database
                continue
            try:
                parsed_trade = TS.load(trade).data
            except ValidationError as e:
                print(e)
            parsed_trade.account_id = user.account.id
            s.add(parsed_trade)
        # update the most recent trade parsed for the account
        if parsed_trade:
            user.account.last_trade = parsed_trade.id
        try:
            s.commit()
        except Exception as e:
            print(e)
            raise

        return


async def update_all_trades(user_id: int):
    """
    Fetches trades for all currency pairs for the user from the beginning of time and stores them in the database
    :param user_id: ID of the user to update
    :return: None
    """
    ...


async def sync_trades(user_id: int):
    """
    Fetches trades all new trades for the user and stores them in the database
    :param user_id: ID fo the user to update
    :return: None
    """
    ...


async def underlying_to_usdt_at_time(underlying_instrument: str, time: int):
    """
    So we should have the USDT value for things traded against USDT. Everything
    :param underlying_instrument: Instrument to query against
    :param time: Epoch time to fetch the price at
    :return: price data at specified time
    """
    with make_binance(api_key='', api_secret='') as exchange:
        data = await exchange.fetch_ohlcv(symbol=underlying_instrument, params={'startTime': time})
    # data = client.get_klines(symbol=underlying_instrument, interval=interval, limit=500, startTime=time,
    #                          endTime=time+60000)
    print(data)
    return data


def get_profit_loss(trade):
    instrument = trade.pair[:3]
    underlying = trade.pair[3:]
    ...


@async_contextmanager
async def make_binance(user: User = None, user_id: int = None, api_key: str = None, api_secret: str = None):
    """
    Yields a Binance exchange object and cleans up afterward
    :param user: user object to get api information from
    :param user_id: ID to look up in the database for api information
    :param api_key: API key
    :param api_secret: API secret
    :return: None
    """
    key = api_key
    secret = api_secret
    if user:
        key = user.api_key
        secret = user.api_secret
    elif user_id:
        with scoped() as s:
            user: User = s.query(User).get(user_id)
            if user:
                key = user.api_key
                secret = user.api_secret

    exchange = binance({'apiKey': key, 'secret': secret, 'enableRateLimit': True,
                        'options': {'adjustForTimeDifference': True}})
    yield exchange
    await exchange.close()
