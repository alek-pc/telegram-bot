import sqlalchemy
from .db_session import SqlAlchemyBase


class List(SqlAlchemyBase):
    __tablename__ = 'lists'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    points = sqlalchemy.Column(sqlalchemy.String, default='')
    members = sqlalchemy.Column(sqlalchemy.String, default='')
