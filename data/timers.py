import sqlalchemy
from .db_session import SqlAlchemyBase


class Timer(SqlAlchemyBase):
    __tablename__ = 'timers'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    hours = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    minutes = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    seconds = sqlalchemy.Column(sqlalchemy.Integer)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
