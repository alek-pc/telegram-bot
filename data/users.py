import sqlalchemy
import datetime
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, unique=True)
    name = sqlalchemy.Column(sqlalchemy.String, default='hz')
    last_visit = sqlalchemy.Column(sqlalchemy.DATETIME, default=datetime.datetime.now())
