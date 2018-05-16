from marshmallow import fields
from marshmallow_sqlalchemy import ModelSchema
from sqlalchemy.orm import scoped_session
from crypto_profit_loss.models.trades import Trade, Fee
from ..database import Session

scoped = scoped_session(Session)


class TradeSchema(ModelSchema):
    user = fields.Nested('UserSchema', many=False)
    fee = fields.Nested('FeeSchema', many=False)

    class Meta:
        model = Trade
        sqla_session = scoped


class FeeSchema(ModelSchema):
    class Meta:
        model = Fee
        sqla_session = scoped
