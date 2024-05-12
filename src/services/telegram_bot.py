import random

import requests
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, CallbackContext
from src.conf import messages
from src.conf.config import settings


async def start(update: Update, context: CallbackContext):
    # Получаем chat_id
    chat_id = update.message.chat.id
    # Выводим chat_id в консоль
    print("Chat ID:", chat_id)
    # Отправляем сообщение приветствия
    await update.message.reply_text(messages.TELEGRAM_WELCOME,
                                    reply_markup=await get_contact_keyboard())


def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/sendMessage"
    params = {
        "chat_id": chat_id,
        "text": text
    }
    response = requests.get(url, params=params)
    return response.json()


async def echo(update: Update, context: CallbackContext):
    # Получаем текст сообщения
    message_text = update.message.text

    # Получаем chat_id
    chat_id = update.message.chat.id

    # Выводим chat_id в консоль
    print("Chat ID:", chat_id)

    # Выводим текст сообщения в консоль
    print("Received message:", message_text)

    # Добавляем текст "_принял" к сообщению
    reply_text = message_text + "_ принял _"

    # Отправляем ответное сообщение с измененным текстом
    await update.message.reply_text(reply_text)


async def status(update: Update, context: CallbackContext):
    # Получаем chat_id
    chat_id = update.message.chat.id
    print("Chat ID:", chat_id)
    # Отправляем статусное сообщение
    await update.message.reply_text(f"Ваш статус: {random.choice(['Ваше авто запарковане', 'Ви до нас не доїхали...'])}")


async def get_contact(update: Update, context: CallbackContext):
    # Получаем номер телефона пользователя
    contact = update.message.contact
    phone_number = contact.phone_number

    # Выводим номер телефона пользователя в консоль
    print("Received phone number:", phone_number)

    # Отправляем сообщение с благодарностью и удаляем клавиатуру
    await update.message.reply_text(f"Спасибо за предоставленный номер телефона: {phone_number}",
                                    reply_markup=ReplyKeyboardRemove())


async def get_contact_keyboard():
    # Создаем клавиатуру для запроса контакта
    keyboard = [[KeyboardButton("Поделиться номером телефона", request_contact=True)]]


    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)


async def balance(update: Update, context: CallbackContext):
    # Получаем chat_id
    chat_id = update.message.chat.id

    # Получаем значение параметра balance (здесь предполагается, что оно хранится где-то в вашем приложении)
    balance_value = get_balance_value()  # Функция get_balance_value() должна быть реализована в вашем коде

    # Отправляем сообщение с текущим значением баланса
    await update.message.reply_text(f"Текущий баланс: {balance_value}")


def get_balance_value():
    curr = "UAH"
    user_balance = 100
    result = f"{user_balance} {curr}"
    return result


def main():
    # Создаем приложение
    app = ApplicationBuilder().token(settings.TELEGRAM_TOKEN).build()

    # Добавляем обработчик команды /start
    app.add_handler(CommandHandler("start", start))

    # Добавляем обработчик команды /status
    app.add_handler(CommandHandler("status", status))

    # Добавляем обработчик команды /balance
    app.add_handler(CommandHandler("balance", balance))

    # Добавляем обработчик сообщений
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Добавляем обработчик запроса контакта
    app.add_handler(MessageHandler(filters.CONTACT, get_contact))

    # Запускаем приложение
    app.run_polling()


