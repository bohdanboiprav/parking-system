import asyncio
from pathlib import Path
import cv2
import datetime


async def capture_and_save_image():
    filename = f'first_cam_{datetime.datetime.now()}.png'
    BASE_DIR = Path(__file__).parent.parent / "static" / "dir_cam_photo"
    filepath = BASE_DIR / filename

    cap = cv2.VideoCapture(1)  # 0 или 1 - в зависимости от количества камер
    await asyncio.sleep(2)
    ret, frame = cap.read()

    if ret:
        cv2.imwrite(str(filepath), frame)
        print(f"Изображение сохранено в {filepath}")
    else:
        print("Не удалось получить кадр с камеры")

    cap.release()
    return filepath


# async def main():
#     await capture_and_save_image(f'first_cam_{datetime.datetime.now()}.png')
