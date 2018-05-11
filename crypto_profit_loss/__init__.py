from crypto_profit_loss.config import API_KEY, API_SECRET, USER_ID
from crypto_profit_loss.schemas.user import UserSchema
from crypto_profit_loss.database import scoped
from crypto_profit_loss.models.user import User
from crypto_profit_loss.utils import update_user


if __name__ == '__main__':
    with scoped() as s:
        if not s.query(User).all():
            s.add(User(first_name='Rich', last_name='Hanson', id=USER_ID,
                       api_key=API_KEY,
                       api_secret=API_SECRET))
            s.commit()
        update_user(USER_ID)
        print(s.query(User).all())



