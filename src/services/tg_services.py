from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func, update
from src.entity.models import User, Avto, Log
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from src.conf.config import settings


async def requests_to_db(request_name, phone=None, chat_id=None):
    result = None
    if request_name:
        # Создаем асинхронный движок
        engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URL)

        # Создаем асинхронную сессию
        Session = sessionmaker(engine, class_=AsyncSession)
        async with Session() as session:

            if request_name == 'find_user_by_phone':
                # Выполняем запрос с условием WHERE
                stmt = select(User.telegram_chat_id).where(User.mobilenamber == phone)
                users_with_phone = await session.execute(stmt)
                # Получаем результаты
                users_with_phone = users_with_phone.first()
                # Выводим результаты
                result = users_with_phone[0]

            elif request_name == 'find_user_by_tg_id':
                # Выполняем запрос с условием WHERE
                stmt = select(User.id).where(User.telegram_chat_id == '164802149')
                users_with_tg_id = await session.execute(stmt)
                # Получаем результаты
                user_with_tg_id = users_with_tg_id.scalar_one_or_none()
                # Возвращаем результат
                result = user_with_tg_id if user_with_tg_id else None

            elif request_name == 'balance':
                # Выполняем запрос с условием WHERE
                stmt = select(User.balance).where(User.mobilenamber == '380664386423')
                balance_result = await session.execute(stmt)
                # Получаем результаты
                balance = balance_result.scalar_one_or_none()
                # Возвращаем результат
                result = balance

            elif request_name == 'status':

                # Выполняем запрос с условием WHERE для нахождения пользователя по telegram_chat_id
                stmt = select(User.id).where(User.telegram_chat_id == '164802149')
                user_with_tg_id = await session.execute(stmt)
                user = user_with_tg_id.scalar_one_or_none()
                if user:
                    # Проверяем, есть ли у пользователя автомобили в таблице Avto
                    avto_count = await session.execute(select(func.count()).where(Avto.user_id == user))
                    avto_count = avto_count.scalar()
                    if avto_count > 0:
                        # Если у пользователя есть автомобили, получаем номера автомобилей
                        avto_numbers = await session.execute(select(Avto.number).where(Avto.user_id == user))
                        avto_numbers = [avto[0] for avto in avto_numbers]

                        # Проверяем статус автомобилей в таблице Log
                        # statuses = []
                        for avto_number in avto_numbers:
                            status = await session.execute(select(Log.in_parking).where(Log.number == avto_number))
                            status = status.scalar_one_or_none()
                            # print(status)
                            # statuses.append(status)
                        # result = statuses
                        result = status
                    else:
                        result = "Нажаль ви не зареєстрували жодного авто"
                else:
                    result = "Нажаль Ви не зареєстровані на нашому сайті"

            elif request_name == 'add_tg_id':
                # Обновляем запись пользователя с указанным номером телефона, добавляя chat_id
                stmt = (
                    update(User)
                    .where(User.mobilenamber == phone)
                    .values(telegram_chat_id=chat_id)
                )
                await session.execute(stmt)
                await session.commit()
                result = f"Додан chat_id {chat_id} для номера телефона {phone}"

    return result
