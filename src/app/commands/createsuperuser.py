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
@click.option("--login", prompt="Enter login", help="Login of the user")
@click.option(
    "--password",
    prompt="Enter password",
    hide_input=True,
    confirmation_prompt=True,
    help="Password of the user",
)
def createsuperuser(login, password) -> str:
    asyncio.run(create_superuser_async(login, password))


async def create_superuser_async(login, password):
    async_engine: AsyncEngine = create_async_engine(
        settings.DSN, echo=settings.LOG_QUERIES
    )
    async_session: async_sessionmaker[AsyncSession] = async_sessionmaker(
        async_engine, expire_on_commit=False
    )

    async with async_session() as session:
        is_exists = await user_repository.exists(session, login=login)

        if is_exists:
            print(f"Superuser {login} already exists.")
            return

        await user_repository.create(
            session,
            {
                "login": login,
                "password": password,
                "is_stuff": True,
                "is_superuser": True,
            },
        )

    print(f"Superuser {login} created.")


if __name__ == "__main__":
    createsuperuser()
