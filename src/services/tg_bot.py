import logging
import requests
from aiogram import Bot, Dispatcher, Router, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.strategy import FSMStrategy
from aiogram.types import ReplyKeyboardRemove
from src.conf import messages
from src.conf.config import settings
from src.services.tg_services import requests_to_db

logging.basicConfig(level=logging.INFO)

bot = Bot(token=settings.TELEGRAM_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
storage = MemoryStorage()
dp = Dispatcher(storage=storage, fsm_strategy=FSMStrategy.USER_IN_CHAT)

router = Router()
dp.include_router(router)


@router.message(CommandStart())
async def start(message: types.Message):
    chat_id = message.chat.id
    logging.info("Chat ID: %s", chat_id)
    button1 = types.KeyboardButton(text="Поділитися номером телефону", request_contact=True)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, keyboard=[[button1]])
    await message.answer(messages.TELEGRAM_WELCOME, reply_markup=keyboard)


@router.message(Command("balance"))
async def command(message: types.Message):
    print(f'Command  ==== >>  {message.text}')
    result = await requests_to_db(message.text[1:])
    await message.answer(f'Ваш баланс: {str(result)}')


@router.message(Command("status"))
async def command(message: types.Message):
    print(f'Status  ==== >>  {message.text}')
    result = await requests_to_db(message.text[1:])
    text_message = 'Ваше авто під нашим доглядом' if result == True else "Нажаль Ваше авто не у нас..."
    await message.answer(text_message)


@router.message(Command("info"))
async def command(message: types.Message):
    print(f'Info  ==== >>  {message.text}')
    text_message = settings.WEBHOOK_URL
    await message.answer(text_message)


@router.message()
async def handle_contact(message: types.Message):
    if message.contact is not None:
        # Получаем информацию о контакте из объекта message
        contact = message.contact
        result = await requests_to_db('find_user_by_phone', phone=contact.phone_number)
        if result == '':
            result = await requests_to_db('add_tg_id', phone=contact.phone_number, chat_id=str(message.chat.id))
            print(result)
        await message.answer("Дякуємо за надану інформацію", reply_markup=ReplyKeyboardRemove())
    else:
        print(f'message.text:   ===>    {message.text}')

    # logging.info("Received contact information: %s", message.contact)
    # await message.answer("Спасибо за предоставленную информацию", reply_markup=ReplyKeyboardRemove())


async def send_message_async(chat_id, text):
    try:
        # Отправляем сообщение
        await bot.send_message(chat_id, text)
        return True
    except Exception as e:
        print("Error sending message:", e)
        return False


def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/sendMessage"
    params = {
        "chat_id": chat_id,
        "text": text
    }
    response = requests.get(url, params=params)
    return response.json()
