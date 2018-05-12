from marshmallow import fields
from marshmallow_sqlalchemy import ModelSchema
from sqlalchemy.orm import scoped_session
from crypto_profit_loss.models.user import User, Balance, BinanceAcct
from ..database import Session

scoped = scoped_session(Session)


class UserSchema(ModelSchema):
    account = fields.Nested('AccountSchema', many=False)

    class Meta:
        model = User
        sqla_session = scoped


class AccountSchema(ModelSchema):
    balances = fields.Nested('BalanceSchema', many=True)

    class Meta:
        model = BinanceAcct
        sqla_session = scoped


class BalanceSchema(ModelSchema):
    class Meta:
        model = Balance
        sqla_session = scoped
