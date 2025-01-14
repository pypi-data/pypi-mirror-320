from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from keyboards import for_index

router = Router(name=__name__)


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Command: /start"""

    await message.answer(
        caption='Hello!',
        reply_markup=for_index.menu()
    )
