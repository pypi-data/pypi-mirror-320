import aiosqlite

async def initialize_db(connection_string: str):
    return await aiosqlite.connect(connection_string)

async def execute_query(db, query: str, params: tuple = ()):
    async with db.execute(query, params) as cursor:
        await db.commit()
        return cursor.lastrowid

async def fetch_all(db, query: str, params: tuple = ()):
    async with db.execute(query, params) as cursor:
        return await cursor.fetchall()

async def fetch_one(db, query: str, params: tuple = ()):
    async with db.execute(query, params) as cursor:
        return await cursor.fetchone()