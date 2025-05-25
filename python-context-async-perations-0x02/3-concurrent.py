import aiosqlite
import asyncio

async def async_fetch_users():
    """Asynchronously fetch all users from the users table."""
    async with aiosqlite.connect(':memory:') as db:
        await db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, age INTEGER)")
        await db.execute("INSERT INTO users (name, email, age) VALUES (?, ?, ?)", ('Alice', 'alice@example.com', 25))
        await db.execute("INSERT INTO users (name, email, age) VALUES (?, ?, ?)", ('Bob', 'bob@example.com', 45))
        await db.execute("INSERT INTO users (name, email, age) VALUES (?, ?, ?)", ('Charlie', 'charlie@example.com', 60))
        await db.commit()
        
        cursor = await db.execute("SELECT * FROM users")
        return await cursor.fetchall()

async def async_fetch_older_users():
    """Asynchronously fetch users older than 40 from the users table."""
    async with aiosqlite.connect(':memory:') as db:
        cursor = await db.execute("SELECT * FROM users WHERE age > 40")
        return await cursor.fetchall()

async def fetch_concurrently():
    """Run both fetch functions concurrently using asyncio.gather."""
    users, older_users = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )
    print("All users:", users)
    print("Users older than 40:", older_users)

# Run the concurrent fetch
asyncio.run(fetch_concurrently())