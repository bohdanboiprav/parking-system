import asyncio
from pathlib import Path
import cv2
import datetime


async def capture_and_save_image(filename):

    BASE_DIR = Path(__file__).parent.parent / "static" / "dir_cam_photo"

    # Полный путь к файлу
    filepath = BASE_DIR / filename
    filepath_str = str(filepath)

    # ВКЛ камеру
    cap = cv2.VideoCapture(0)  # 0 или 1 - в зависимости от количества камер

    # Ожидание получения кадра
    await asyncio.sleep(2)

    # Сделать снимок
    ret, frame = cap.read()

    # Запись файла
    if ret:
        cv2.imwrite(filepath_str, frame)
        print(f"Изображение сохранено в {filepath_str}")
    else:
        print("Не удалось получить кадр с камеры")

    # ВЫКЛ камеру
    cap.release()


async def main():
    await capture_and_save_image(f'first_cam_{datetime.datetime.now()}.png')

# Запуск асинхронной функции
asyncio.run(main())
