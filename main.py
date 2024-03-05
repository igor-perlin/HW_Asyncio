import aiohttp
import aiosqlite
import asyncio

async def init_db(db_path):
    async with aiosqlite.connect(db_path) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS characters (
                id TEXT PRIMARY KEY,
                birth_year TEXT,
                eye_color TEXT,
                films TEXT,
                gender TEXT,
                hair_color TEXT,
                height TEXT,
                homeworld TEXT,
                mass TEXT,
                name TEXT,
                skin_color TEXT,
                species TEXT,
                starships TEXT,
                vehicles TEXT
            );
        """)
        await db.commit()

async def fetch_character(session, url):
    async with session.get(url) as response:
        return await response.json()

async def save_character_to_db(db, character):
    character_id = character['url'].split('/')[-2]
    # Пример обработки списка films, для остальных полей аналогично
    films = ','.join([film.split('/')[-2] for film in character['films']])
    # Для species, starships, vehicles аналогично
    async with db.execute(
        "INSERT INTO characters (id, birth_year, eye_color, films, gender, hair_color, height, homeworld, mass, name, skin_color, species, starships, vehicles) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (character_id, character['birth_year'], character['eye_color'], films, character['gender'], character['hair_color'], character['height'], character['homeworld'], character['mass'], character['name'], character['skin_color'], ','.join(character['species']), ','.join(character['starships']), ','.join(character['vehicles']))
    ):
        await db.commit()

async def main():
    await init_db('swapi.db')
    async with aiosqlite.connect('swapi.db') as db, aiohttp.ClientSession() as session:
        for i in range(1, 84):  # SWAPI содержит информацию о 83 персонажах
            character = await fetch_character(session, f'https://swapi.dev/api/people/{i}/')
            if 'detail' in character and character['detail'] == 'Not found':
                continue
            await save_character_to_db(db, character)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
