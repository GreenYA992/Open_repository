from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker

class Connection:
    def __init__(self, sql_type, user, password, server, port=None, **args) -> None:
        self.sql_type = sql_type
        self.user = user
        self.password = password
        self.server = server
        self.port = port
        self.args = args
    @property
    def engine(self):
        if self.sql_type == 'MSSQL':
            return (f'mssql+pymssql://{self.user}:{self.password}'
                    f'@{self.server}/{self.args['db_name']}')
        if self.sql_type == 'PostgresSQL':
            return (f'postgresql://{self.user}:{self.password}'
                    f'@{self.server}:{str(self.port)}/{self.args['db_name']}')
        print('Соединение не поддерживается')
        return None
    @property
    def async_engine(self):
        if self.sql_type == 'MSSQL':
            return (f'mssql+aioodbc://{self.user}:'
                    f'{self.password}@{self.server}/{self.args['db_name']}')
        if self.sql_type == 'PostgresSQL':
            return (f'postgresql+asyncpg://{self.user}:'
                    f'{self.password}@{self.server}:{str(self.port)}/{self.args['db_name']}')
        print('Соединение не поддерживается')
        return None

class SessionBuilder:
    def __init__(self, connection: Connection):
        self.engine = create_engine(connection.engine)
        self.async_engine = create_async_engine(connection.async_engine)
    def build(self) -> sessionmaker:
        return sessionmaker(bind = self.engine)
    def async_build(self) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(bind = self.async_engine, class_ = AsyncSession, expire_on_commit = False)


class AsyncSessionBuilder:
    def __init__(self, connection: Connection):
        self.async_engine = create_async_engine(
            connection.async_engine, echo=True)
    def async_build(self) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(bind=self.async_engine, class_=AsyncSession, expire_on_commit=False)


connection = Connection(
        server='localhost',
        port=5432,
        user='postgres',
        password='password',
        db_name='Project',
        sql_type='PostgresSQL')

engine = SessionBuilder(connection)
session_factory = engine.build()

async_engine = AsyncSessionBuilder(connection)
async_session_factory = async_engine.async_build()
