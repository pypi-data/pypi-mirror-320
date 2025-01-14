import motor.motor_asyncio
from settings import Settings
from redis.asyncio import Redis
from interface.user import IUser

class ObjectNotFound(Exception):
    pass

settings = Settings()
redis = Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_db,
)

class Database:
    def __init__(self, url_connect: str = None):
        self.cluster = motor.motor_asyncio.AsyncIOMotorClient(url_connect).cluster.TelegramBot

        self.users_collection = self.cluster.user

    async def create_user(self, user_id: int, username: str, first_name: str, last_name: str) -> IUser:
        """
        Create a new user

        :param user_id: Telegram user id
        :return:
        """

        data = IUser(
            user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )

        await self.users_collection.insert_one(data.model_dump())
        return data

    async def get_user(self, user_id: int) -> IUser:
        """
        Get a user

        :param user_id: Telegram user id
        :return:
        """

        data = await self.users_collection.find_one({'user_id': user_id})
        if data:
            return IUser(**data)
        raise ObjectNotFound()

db = Database(settings.mongodb_url.get_secret_value())
