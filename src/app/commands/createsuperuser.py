import asyncio

import click
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.repository.user import user_repository
from app.settings.postgresql import settings


@click.command()
@click.option("--username", prompt="Enter username", help="Username")
@click.option(
    "--password",
    prompt="Enter password",
    hide_input=True,
    confirmation_prompt=True,
    help="Password of the user",
)
def createsuperuser(username, password) -> str:
    asyncio.run(create_superuser_async(username, password))


async def create_superuser_async(username, password):
    async_engine: AsyncEngine = create_async_engine(
        settings.DSN, echo=settings.LOG_QUERIES
    )
    async_session: async_sessionmaker[AsyncSession] = async_sessionmaker(
        async_engine, expire_on_commit=False
    )

    async with async_session() as session:
        is_exists = await user_repository.exists(session, username=username)

        if is_exists:
            print(f"Superuser {username} already exists.")
            return

        await user_repository.create(
            session,
            {
                "username": username,
                "password": password,
                "is_stuff": True,
                "is_superuser": True,
            },
        )

    print(f"Superuser {username} created.")


if __name__ == "__main__":
    createsuperuser()
