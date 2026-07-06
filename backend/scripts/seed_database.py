import asyncio

from app.bootstrap import seed_database


async def main() -> None:
    created = await seed_database()
    print("Seed complete:", created)


if __name__ == "__main__":
    asyncio.run(main())
